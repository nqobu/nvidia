import pyfaidx
import numpy as np
import polars as pl
import pandas as pd
from Bio.Data import CodonTable
from scripts.gtf_processing import extract_cds_sequence, check_cds_quality

def extract_cds(REFERENCE_GENOME,
                ANNOTATION_FILE,
                FILTERED_TRANSCRIPTS_FILE):
    
    # Valid chromosomes for analysis
    VALID_CHROMS = [f'chr{i}' for i in range(1, 23)] + ['chrX']

    # DNA complement mapping for reverse complement operations
    COMPLEMENT = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N'}

    print(f"Reference genome: {REFERENCE_GENOME}")
    print(f"Annotation file: {ANNOTATION_FILE}")
    print(f"Output file: {FILTERED_TRANSCRIPTS_FILE}")

    # =============================================================================
    # Load Reference Genome (GRCh38/hg38)
    # =============================================================================
    # Pre-load chromosome sequences into memory for faster access during variant generation.
    # Only loading standard chromosomes (1-22, X, Y) - excluding patches and alternate contigs.

    fasta = {}

    with pyfaidx.Fasta(REFERENCE_GENOME) as f:
        for chrom in VALID_CHROMS:
            fasta[chrom] = f[chrom][:].seq
    print(f"Loaded {len(fasta)} chromosomes from {REFERENCE_GENOME}")

    # =============================================================================
    # Load Annotations, Extract CDS Sequences, and Apply Quality Filters
    # =============================================================================

    # -----------------------------------------------------------------------------
    # Step 1: Load processed GENCODE annotation
    # -----------------------------------------------------------------------------
    # Input: TSV file from the processing above containing
    # transcript coordinates, exon boundaries, and canonical status flags
    ann = pl.read_csv(ANNOTATION_FILE, separator='\t')
    ann = ann.filter(pl.col('chrom').is_in(VALID_CHROMS))
    print(f"Loaded {len(ann):,} transcripts from {ANNOTATION_FILE}")

    # -----------------------------------------------------------------------------
    # Step 2: Deduplicate transcripts with identical genomic structure
    # -----------------------------------------------------------------------------
    # Multiple transcript IDs can map to the same CDS coordinates (e.g., RefSeq vs Ensembl)
    # Keep MANE Select > Ensembl Canonical when duplicates exist
    ann = ann.sort(['is_mane_select', 'is_canonical'], descending=True)
    ann = ann.unique(subset=['chrom', 'strand', 'cdsStart', 'cdsEnd', 'exonStarts', 'exonEnds'])
    print(f"After deduplicating by genomic structure: {len(ann):,} transcripts")

    # -----------------------------------------------------------------------------
    # Step 3: Extract CDS sequences from reference genome
    # -----------------------------------------------------------------------------
    print("Extracting CDS sequences...")
    sequences = [extract_cds_sequence(row, fasta) for row in ann.iter_rows(named=True)]
    ann = ann.with_columns(pl.Series("cds_sequence", sequences))

    # -----------------------------------------------------------------------------
    # Step 4: Quality control - validate CDS sequences
    # -----------------------------------------------------------------------------
    print("Running quality checks...")
    quality_checks = [check_cds_quality(row['cds_sequence']) for row in ann.iter_rows(named=True)]

    ann = ann.with_columns([
        pl.Series("has_start_codon", [q['has_start_codon'] for q in quality_checks]),
        pl.Series("has_stop_codon", [q['has_stop_codon'] for q in quality_checks]),
        pl.Series("length_divisible_by_3", [q['length_divisible_by_3'] for q in quality_checks]),
        pl.Series("has_internal_stop_codons", [q['has_internal_stop_codons'] for q in quality_checks]),
        pl.Series("cds_length", [q['length'] for q in quality_checks])
    ])

    # Print quality summary
    print("\n" + "="*60)
    print("CDS Quality Summary (before filtering):")
    print("="*60)
    print(f"Total transcripts: {len(ann):,}")
    print(f"Has start codon (ATG): {ann['has_start_codon'].sum():,} ({ann['has_start_codon'].mean()*100:.1f}%)")
    print(f"Has stop codon (TAA/TAG/TGA): {ann['has_stop_codon'].sum():,} ({ann['has_stop_codon'].mean()*100:.1f}%)")
    print(f"Length divisible by 3: {ann['length_divisible_by_3'].sum():,} ({ann['length_divisible_by_3'].mean()*100:.1f}%)")
    print(f"Has internal stop codons: {ann['has_internal_stop_codons'].sum():,} ({ann['has_internal_stop_codons'].mean()*100:.1f}%)")
    print(f"All quality criteria met: {(ann['has_start_codon'] & ann['has_stop_codon'] & ann['length_divisible_by_3'] & ~ann['has_internal_stop_codons']).sum():,}")

    # -----------------------------------------------------------------------------
    # Step 5: Apply quality filters
    # -----------------------------------------------------------------------------
    # Keep only transcripts that pass all quality checks
    ann = ann.filter(
        pl.col('has_start_codon') & 
        pl.col('has_stop_codon') & 
        pl.col('length_divisible_by_3') & 
        ~pl.col('has_internal_stop_codons')
    )
    print(f"\nAfter quality filtering: {len(ann):,} transcripts")

    # -----------------------------------------------------------------------------
    # Step 6: Filter to canonical transcripts and deduplicate by CDS sequence
    # -----------------------------------------------------------------------------
    # Keep only MANE Select or Ensembl Canonical transcripts
    # Then deduplicate by CDS sequence (different transcripts can encode identical proteins)
    initial_count = len(ann)
    ann = ann.filter(pl.col('is_mane_select') | pl.col('is_canonical'))
    print(f"After filtering to canonical transcripts: {len(ann):,} transcripts")

    ann = ann.sort(['is_mane_select', 'is_canonical'], descending=True)
    ann = ann.unique(subset=['cds_sequence'], keep='first')
    ann = ann.sort(['chrom', 'txStart'])

    print(f"After canonical filter + CDS deduplication: {len(ann):,} unique transcripts")
    print(f"  (Removed {initial_count - len(ann):,} transcripts)")
    ann.write_csv(FILTERED_TRANSCRIPTS_FILE, separator='\t')
    print(f"Saved {len(ann):,} unique transcripts to {FILTERED_TRANSCRIPTS_FILE}")

def reverse_complement_dna(seq):
    """
    Return the reverse complement of a DNA sequence.
    
    Parameters:
        seq (str): A DNA sequence with uppercase letters only (e.g., "ATCG").
    
    Returns:
        str: The reverse complement DNA sequence.
        
    Raises:
        KeyError: If the sequence contains lowercase letters or invalid characters.
    """
    complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N'}
    return ''.join(complement[base] for base in seq[::-1].upper())

def map_variants_to_genes_by_exons_efficient(genes_df, variants_df, variant_columns=['pos', 'ref', 'alt', 'af', 'ac', 'an']):
    """
    Efficient mapping using sorted variants and binary search for range queries.
    """
    import bisect
    
    gene_variant_mapping = {}
    
    print(f"Processing {len(genes_df)} genes and {len(variants_df)} variants...")
    
    # Pre-sort variants by chromosome and position for efficient range queries
    chrom_sorted_variants = {}
    unique_chroms = variants_df.select('chrom').unique().to_series().to_list()
    
    for chrom in unique_chroms:
        chrom_variants = variants_df.filter(pl.col('chrom') == chrom).sort('pos')
        if len(chrom_variants) > 0:
            # Extract positions and variant data separately for efficient binary search
            positions = chrom_variants.select('pos').to_series().to_numpy() - 1
            variant_data = chrom_variants.select(variant_columns).to_dicts()
            chrom_sorted_variants[chrom] = (positions, variant_data)
    
    # Process genes
    for gene_row in genes_df.iter_rows(named=True):
        id = gene_row['id']
        chrom = gene_row['chrom']
        strand = gene_row['strand']
        cds_seq = gene_row['cds_sequence']
        
        gene_variant_mapping[id] = {
            'variants': []
        }
        
        if chrom not in chrom_sorted_variants:
            continue
            
        positions, variant_data = chrom_sorted_variants[chrom]
        
        # Parse exon coordinates
        exon_starts = gene_row['exonStarts']
        exon_ends = gene_row['exonEnds']
        cds_start = gene_row['cdsStart']
        cds_end = gene_row['cdsEnd']
        
        if exon_starts and exon_ends:
            if isinstance(exon_starts, str):
                starts = [int(x.strip()) for x in exon_starts.split(',') if x.strip()]
            else:
                starts = [int(exon_starts)]
                
            if strand == '-':
                assert starts[0] == cds_start, f'{cds_start}, {starts[0]}, {gene_row["id"]}, {gene_row["gene_id"]}'
                starts[0] = cds_start

            if isinstance(exon_ends, str):
                ends = [int(x.strip()) for x in exon_ends.split(',') if x.strip()]
            else:
                ends = [int(exon_ends)]
            if strand == '+':
                assert ends[-1] == cds_end, f'{cds_end}, {ends[-1]}, {gene_row["id"]}, {gene_row["gene_id"]}'
                ends[-1] = cds_end
        else:
            raise ValueError(f"No exon coordinates found for gene {id}")
        assert starts[0] == cds_start and ends[-1] == cds_end
        # Use binary search to find variants in each exon range
        cum_left = 0
        for start, end in zip(starts, ends):
            # Find range of variants within [start, end] using binary search
            left_idx = bisect.bisect_left(positions, start)
            right_idx = bisect.bisect_left(positions, end)
            
            # Extract variants in this range
            for i in range(left_idx, right_idx):
                variant = variant_data[i].copy()
                variant['chrom'] = chrom
                variant['exon_start'] = start
                variant['exon_end'] = end
                dist_left = cum_left + variant['pos'] - 1 - start
                dist_in_cds = dist_left if strand == '+' else len(cds_seq) - dist_left - 1
                variant['dist_left'] = dist_left
                variant['dist_in_cds'] = dist_in_cds
                codon_start = dist_in_cds // 3 * 3
                variant['ref_codon'] = cds_seq[codon_start:codon_start+3]
                alt_codon = []
                for j in range(3):
                    if j + codon_start != dist_in_cds:
                        alt_codon.append(variant['ref_codon'][j])
                    else:
                        if strand == '+':
                            assert variant['ref'].upper() == cds_seq[j+codon_start].upper()
                            alt_codon.append(variant['alt'].upper())
                        else:
                            assert variant['ref'].upper() == reverse_complement_dna(cds_seq[j+codon_start]).upper()
                            alt_codon.append(reverse_complement_dna(variant['alt'].upper()))
                variant['alt_codon'] = ''.join(alt_codon)
                gene_variant_mapping[id]['variants'].append(variant)
            cum_left += end - start
    
    return gene_variant_mapping

def get_alt_seq(row):
    ref_seq, ref_codon, alt_codon, codon_pos = row['ref_seq'], row['ref_codon'], row['alt_codon'], row['codon_position']
    assert codon_pos >= 0 and codon_pos < len(ref_seq) / 3
    assert ref_seq[codon_pos*3:(codon_pos+1)*3] == ref_codon
    alt_seq = ref_seq[:codon_pos*3] + alt_codon + ref_seq[(codon_pos+1)*3:]
    return alt_seq


def translate(seq):
    """
    Translate an RNA sequence into a protein sequence.
    """
    protein = ""
    # Process the RNA sequence three nucleotides (codon) at a time.
    for i in range(0, len(seq) - 2, 3):
        codon = seq[i : i + 3]
        # Look up the codon in the genetic code dictionary.
        amino_acid = codon_to_aa(codon)
        protein += amino_acid if amino_acid is not None else "?"
    return protein


def codon_to_aa(codon):
    """
    Translate a single codon to its corresponding amino acid using BioPython's CodonTable.
    
    Parameters:
        codon (str): A 3-nucleotide DNA codon.
    
    Returns:
        str or None: The single-letter amino acid code, '*' for stop codons, or None if invalid.
    """
    standard_table = CodonTable.unambiguous_dna_by_name["Standard"]
    codon = codon.upper().replace('U', 'T')
    if len(codon) != 3 or any(base not in "ATGC" for base in codon):
        return None
    if codon in standard_table.stop_codons:
        return '*'
    return standard_table.forward_table.get(codon, None)


def reverse_complement_dna(seq):
    """
    Return the reverse complement of a DNA sequence.
    
    Parameters:
        seq (str): A DNA sequence with uppercase letters only (e.g., "ATCG").
    
    Returns:
        str: The reverse complement DNA sequence.
        
    Raises:
        KeyError: If the sequence contains lowercase letters or invalid characters.
    """
    complement = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N'}
    return ''.join(complement[base] for base in seq[::-1].upper())

def process_a_chrom(chrom_variants, chrom_refseq, return_alt_cds=False):
    """
    Annotate a single nucleotide variant with transcript CDS context.
        - Locate its position within the coding sequence (0-based coordinate),
        - extract the ref codon and build the alt codon,
        - translate codons to amino acids,
        - optionally, build the full alternate CDS with the mutation.
    
    ## Notes: The output columns are: 
       - pos: 1-based (forward direction, genomic coordinates)
       - ref: genomic ref allele (as in the reference genome, forward orientation)
       - alt: genomic alt allele (as in the reference genome, forward orientation)
       - cdsStart: 0-based genomic start of CDS, half-open interval; genomic axis.
       - cdsEnd: 0-based genomic end of CDS, half-open interval; genomic axis.
       - var_rel_dist_in_cds: 0-based index within the CDS in transcript 5'->3' orientation (strand-aware).
       - ref_seq: full CDS string in transcript 5'->3' orientation
       - ref_codon: codon from ref_seq at the variant position; strand-aware.
       - alt_codon: codon after single-base change; strand-aware.
       - ref_aa: ref amino acid at the variant position
       - alt_aa: alt amino acid at the variant position
       - alt_seq (if set): full alt CDS after the single-base change, transcript 5'->3' orientation; strand-aware.
       - codon_position: 0-based codon index within CDS.

    """
    # normalize alleles;
    chrom_variants['ref'] = chrom_variants['ref'].str.upper()
    chrom_variants['alt'] = chrom_variants['alt'].str.upper()


    var_ids = chrom_variants['variant_id'].values
    var_pos = chrom_variants['pos'].values - 1  # Convert to 0-based - mutations are always reported in 1-based coordinates
    var_ref = chrom_variants['ref'].values # reference allele
    var_alt = chrom_variants['alt'].values # alternate allele
    chrom = chrom_refseq.iloc[0]['chrom']
    
    # CDS processed using `process_gtf`` function
    cds_strands = chrom_refseq['strand'].values # strand of the coding sequence
    cds_starts = chrom_refseq['cdsStart'].values  
    cds_ends = chrom_refseq['cdsEnd'].values
    cds_lengths = chrom_refseq['cds_length'].values
    rec_cds_starts = chrom_refseq['cds_starts'].values  # List of exon starts within the CDS region for all transcripts.
    rec_cds_ends = chrom_refseq['cds_ends'].values  # List of exon ends within the CDS region for all transcripts.
    rec_cds = chrom_refseq['cds'].values  # CDS sequence - strand-aware (always gene 5'->3')
    rec_names = chrom_refseq['name'].values

    # Find transcripts (CDS regions)that overlap the variant position
    # sorted variant positions to find, per transcript, 
    # var_pos[s1[j]:ss2[j]] includes all variants with pos in [cdsStart[j], cdsEnd[j]) for transcript j. 
    s1 = np.searchsorted(var_pos, cds_starts, side='left')
    s2 = np.searchsorted(var_pos, cds_ends, side='right')
    results = []

    # Loop through each transcript j (CDS region) and get information for all overlapping variants.
    for j, (ss1, ss2) in enumerate(zip(s1, s2)):
        curr_starts = rec_cds_starts[j] # CDS starts boundaries for transcript j.
        curr_ends = rec_cds_ends[j] # CDS ends boundaries for transcript j.
        # Sanity checks on CDS sequence for this transcript
        assert cds_lengths[j] == len(rec_cds[j]), f"CDS length mismatch for {rec_names[j]}"
        assert cds_lengths[j] % 3 == 0, f"CDS length not multiple of 3 for {rec_names[j]}"
        if ss1 < ss2:
            for i in range(ss1, ss2): # loop through all variants in the CDS region for transcript j.
                pos = var_pos[i]
                curr_ref = var_ref[i]
                curr_alt = var_alt[i]
                # Calculate offset in CDS sequence - translate a genomic coordinate into a CDS relativeindex.
                offset = 0
                bound = False
                for a,b in zip(curr_starts, curr_ends):
                    if pos >= b: # if the variant is after the end of the exon
                        offset += b-a  # Add length of complete exon
                    elif a <= pos < b:
                        offset += pos-a 
                        bound = True  # the variant is within this exon
                        break
                if bound:
                    if cds_strands[j] == '-':
                        # Handle reverse strand
                        offset = cds_lengths[j]-1-offset  # Convert to reverse strand position
                        ref_codon = rec_cds[j][offset//3*3:offset//3*3+3]
                        # Check if the reference base in ref codon is the reverse complement of the variant reference allele from the reference FASTA.
                        assert rec_cds[j][offset] == reverse_complement_dna(curr_ref), f'-, {ref_codon} {var_ids[i]}'
                        # Build the alternate codon by replacing the reference base with the alternate allele.
                        alt_codon = ref_codon[:offset%3] + reverse_complement_dna(curr_alt) + ref_codon[offset%3+1:]
                        results.append([chrom, pos, f'{chrom}_{pos+1}_{curr_ref}_{curr_alt}', curr_ref, curr_alt,
                                     rec_names[j], cds_starts[j], cds_ends[j], cds_strands[j], offset, rec_cds[j],
                                     ref_codon, alt_codon, translate(ref_codon), translate(alt_codon)])
                        
                        if return_alt_cds:
                            alt_cds = rec_cds[j][:offset] + reverse_complement_dna(curr_alt) + rec_cds[j][offset+1:]
                            results[-1].append(alt_cds)
                    else:
                        # Handle forward strand
                        ref_codon = rec_cds[j][offset//3*3:offset//3*3+3]
                        assert rec_cds[j][offset] == curr_ref, f'+, {ref_codon} {var_ids[i]}'
                        alt_codon = ref_codon[:offset%3] + curr_alt + ref_codon[offset%3+1:]
                        
                        results.append([chrom, pos, f'{chrom}_{pos+1}_{curr_ref}_{curr_alt}', curr_ref, curr_alt,
                                     rec_names[j], cds_starts[j], cds_ends[j], cds_strands[j], offset, rec_cds[j],
                                     ref_codon, alt_codon, translate(ref_codon), translate(alt_codon)])
                        
                        if return_alt_cds:
                            alt_cds = rec_cds[j][:offset] + curr_alt + rec_cds[j][offset+1:]
                            results[-1].append(alt_cds)

    columns = ['chrom','pos','variant_id','ref','alt','tx_name', 'cdsStart','cdsEnd','tx_strand',
              'var_rel_dist_in_cds', 'ref_seq','ref_codon','alt_codon','ref_aa','alt_aa']
    if return_alt_cds:
        columns.append('alt_seq')
    
    if results:
        results = pd.DataFrame(results)
        results.columns = columns
        results['pos'] += 1  # Convert back to 1-based
        results['codon_position'] = results['var_rel_dist_in_cds']//3
    else:
        # Create empty DataFrame with correct columns
        results = pd.DataFrame(columns=columns)
        results['codon_position'] = pd.Series(dtype='int64')

    return results

def check_mutation_positions(df: pd.DataFrame, adjusted_context_length: int) -> pd.DataFrame:
    """
    Check if the mutation positions are within the bounds of the coding sequence.
    adjusted_context_length = max_length - 2 (for [CLS] and [SEP])
    """
    def _check(row):
        ref_seq = row["ref_seq"]
        codon_pos = int(row["codon_position"])
        total_codons = (len(ref_seq) // 3) if isinstance(ref_seq, str) else 0
        out = {
            "id": row.get("id", None),
            "variant_id": row.get("variant_id", None),
            "total_codons": total_codons,
            "codon_position": codon_pos,
            "in_bounds": codon_pos < total_codons,
            "needs_centering": total_codons > adjusted_context_length,
            "out_of_bounds": codon_pos >= adjusted_context_length,
        }
        return pd.Series(out)
    return df.apply(_check, axis=1)

def convert_gene_variant_mapping_to_df(gene_variant_mapping, genes, extra_cols=[]):
    # Flatten gene_variant_mapping into a list of variant dicts, each with gene id
    variant_rows = []
    for row_id, info in gene_variant_mapping.items():
        for variant in info['variants']:
            row = variant.copy()
            row['row_id'] = row_id
            variant_rows.append(row)

    gene_variant_df = pd.DataFrame(variant_rows)
    gene_variant_df['codon_pos'] = gene_variant_df['dist_in_cds'] // 3

    # Compute ref_aa and alt_aa columns
    gene_variant_df['ref_aa'] = gene_variant_df['ref_codon'].apply(lambda c: codon_to_aa(c) if pd.notnull(c) else None)
    gene_variant_df['alt_aa'] = gene_variant_df['alt_codon'].apply(lambda c: codon_to_aa(c) if pd.notnull(c) else None)

    # Compute is_synonymous column
    gene_variant_df['is_synonymous'] = gene_variant_df.apply(
        lambda row: (
            row['ref_aa'] == row['alt_aa']
            if pd.notnull(row['ref_aa']) and pd.notnull(row['alt_aa']) and (row['ref_aa'] != '*') else False
        ),
        axis=1
    )

    gene_variant_df = pl.from_pandas(gene_variant_df)

    temp = gene_variant_df.with_columns(
        pl.col('row_id').cast(pl.Int64)
    ).join(genes.select(['id', 'gene_name', 'name', 'gene_id', 'cds_sequence','strand']), left_on='row_id', right_on='id')
    cols_to_select = ['chrom', 'pos', 'ref', 'alt', 'ref_codon', 'alt_codon', 'gene_name', 'gene_id', 'cds_sequence','strand', 'codon_pos', 'dist_in_cds']
    if extra_cols:
        cols_to_select += [x for x in extra_cols if x not in ['chrom', 'pos', 'ref', 'alt']]
    temp = temp.select(cols_to_select)
    result = temp.sort('chrom', 'pos').with_row_index('id').rename(
        {
            'cds_sequence': 'ref_seq',
            'codon_pos': 'codon_position',
            'dist_in_cds': 'var_rel_dist_in_cds'
        }
    )
    
    result = result.with_columns(
        pl.struct(pl.col('ref_seq'), pl.col('ref_codon'), pl.col('alt_codon'), pl.col('codon_position')).map_elements(get_alt_seq, return_dtype=pl.Utf8).alias('alt_seq')
    )

    return result

