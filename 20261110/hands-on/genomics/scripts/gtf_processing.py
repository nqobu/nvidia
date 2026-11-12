# Helper functions to validate and adjust CDS (coding sequence) boundaries
# These functions ensure that the exon coordinates properly include the stop codon (3 bp)

import polars as pl

def check_start_alignment(row):
    """
    Validates that CDS start aligns with exon start and adjusts for stop codon on minus strand.
    For minus strand genes, the stop codon is at the 3' end (lowest genomic position), so we subtract 3 bp.
    """
    cds_start = row['cds_start']
    exon_starts = list(map(int, row['exon_starts'].strip(',').split(',')))
    if row['strand'] == '-':
        # Extend first exon by 3 bp to include stop codon (on minus strand)
        exon_starts[0] -= 3
    assert cds_start == exon_starts[0], f"{cds_start} != {exon_starts[0]} {row['transcript_id']}"

    exon_starts = ','.join(map(str, exon_starts)) + ','
    return exon_starts

def check_end_alignment(row):
    """
    Validates that CDS end aligns with exon end and adjusts for stop codon on plus strand.
    For plus strand genes, the stop codon is at the 3' end (highest genomic position), so we add 3 bp.
    """
    cds_end = row['cds_end']
    exon_ends = list(map(int, row['exon_ends'].strip(',').split(',')))
    if row['strand'] == '+':
        # Extend last exon by 3 bp to include stop codon (on plus strand)
        exon_ends[-1] += 3
    assert cds_end == exon_ends[-1], f"{cds_end} != {exon_ends[-1]} {row['transcript_id']}"

    exon_ends = ','.join(map(str, exon_ends)) + ','
    return exon_ends

def process_gtf_file(gtf_file, output_file):
    """
    Process a GENCODE GTF file and extract protein-coding transcript annotations.
    
    This function:
    1. Parses the GTF file and extracts relevant attributes
    2. Filters for protein-coding genes only
    3. Aggregates exon/CDS coordinates per transcript
    4. Adjusts coordinates to include stop codons
    5. Outputs a tab-separated file with transcript annotations
    
    Args:
        gtf_file: Path to input GENCODE GTF file (can be gzipped)
        output_file: Path for output TSV file
    """
    # Read GTF file (standard 9-column format)
    gtf = pl.read_csv(gtf_file, comment_prefix='#', separator='\t', has_header=False)
    gtf.columns = ['chrom', 'source', 'feature', 'start', 'end', 'score', 'strand', 'frame', 'attribute']
    
    # Parse the attribute column (column 9) to extract key-value pairs
    # GTF attributes are semicolon-separated with format: key "value"
    gtf = gtf.with_columns([
        pl.col('attribute').str.extract('gene_id "(.*?)"', 1).alias('gene_id'),
        pl.col('attribute').str.extract('transcript_id "(.*?)"', 1).alias('transcript_id'),
        pl.col('attribute').str.extract('gene_name "(.*?)"', 1).alias('gene_name'),
        pl.col('attribute').str.extract('gene_type "(.*?)"', 1).alias('gene_type'),
        pl.col('attribute').str.extract('transcript_type "(.*?)"', 1).alias('transcript_type'),
        pl.col('attribute').str.extract('exon_number (.*?);', 1).alias('exon_number')
    ])
    
    # Flag canonical transcripts (Ensembl canonical and MANE Select)
    gtf = gtf.with_columns(pl.col('attribute').str.contains('Ensembl_canonical').alias('is_canonical'))
    gtf = gtf.with_columns(pl.col('attribute').str.contains('MANE_Select').alias('is_mane_select'))
    
    # Filter to protein-coding genes only, exclude gene-level features
    protein_coding_gtf = gtf.filter((pl.col('gene_type') == 'protein_coding') & (pl.col('feature') != 'gene'))
    # Filter to protein-coding transcripts only
    protein_coding_gtf = protein_coding_gtf.filter(pl.col('transcript_type') == 'protein_coding')
    
    # Convert from 1-based (GTF) to 0-based coordinates (BED-like format)
    protein_coding_gtf = protein_coding_gtf.with_columns(pl.col('start') - 1)
    
    # Aggregate CDS exon coordinates per transcript
    # Creates comma-separated lists of exon start/end positions (sorted by genomic position)
    exon_starts = protein_coding_gtf.filter(pl.col('feature') == 'CDS').group_by('transcript_id').agg(
        (pl.col('start').sort().cast(str).str.join(',') + ',').alias('exon_starts'),
        (pl.col('end').sort().cast(str).str.join(',') + ',').alias('exon_ends'),
        pl.col('exon_number').max().alias('exon_count')
    )
    
    # Calculate CDS boundaries with stop codon adjustment
    # GENCODE GTF excludes stop codon from CDS, but we want to include it
    # For + strand: stop codon is after the last CDS position (add 3 to max end)
    # For - strand: stop codon is before the first CDS position (subtract 3 from min start)
    # Note: Using min()/max() instead of first()/last() to avoid dependency on row order
    cds_starts = protein_coding_gtf.filter(pl.col('feature') == 'CDS').group_by('transcript_id').agg(
        pl.when(pl.col('strand').first() == '-')
        .then(pl.col('start').min() - 3)  # Include stop codon at 3' end (lowest genomic position)
        .otherwise(pl.col('start').min())  # 5' end, no adjustment needed
        .alias('cds_start'),
        pl.when(pl.col('strand').first() == '-')
        .then(pl.col('end').max())  # 5' end (highest genomic position), no adjustment
        .otherwise(pl.col('end').max() + 3)  # Include stop codon at 3' end
        .alias('cds_end'),
    )
    
    # Get transcript-level metadata (gene info, coordinates, canonical status)
    tx_starts = protein_coding_gtf.filter(pl.col('feature') == 'transcript').group_by('transcript_id').agg(
        pl.col('gene_id').first().alias('gene_id'),
        pl.col('gene_name').first().alias('gene_name'),
        pl.col('chrom').first().alias('chrom'),
        pl.col('strand').first().alias('strand'),
        pl.col('start').min().alias('tx_start'),
        pl.col('end').max().alias('tx_end'),
        pl.col('transcript_type').first().alias('transcript_type'),
        pl.col('is_canonical').first().alias('is_canonical'),
        pl.col('is_mane_select').first().alias('is_mane_select'),
    )
    
    # Join all transcript information together
    joined_df = tx_starts.join(cds_starts, on='transcript_id', how='inner')\
                        .join(exon_starts, on='transcript_id', how='inner')
    
    # Validate and adjust exon coordinates to include stop codon
    joined_df = joined_df.with_columns(
        pl.struct(['cds_start', 'exon_starts', 'strand', 'transcript_id']).map_elements(check_start_alignment, return_dtype=pl.Utf8).alias('exon_starts'),
        pl.struct(['cds_end', 'exon_ends', 'strand', 'transcript_id']).map_elements(check_end_alignment, return_dtype=pl.Utf8).alias('exon_ends')
    )
    
    # Sort by chromosome and position, then select and rename columns for output
    joined_df = joined_df.sort(['chrom', 'tx_start'])
    joined_df = joined_df.select([
        'gene_id',
        'transcript_id',
        'chrom',
        'strand',
        'tx_start',
        'tx_end', 
        'cds_start',
        'cds_end',
        'exon_count',
        'exon_starts',
        'exon_ends',
        'gene_name',
        'transcript_type',
        'is_canonical',
        'is_mane_select'
    ]).rename({
        'transcript_id': 'name',        # Transcript ID becomes the 'name' field
        'tx_start': 'txStart',          # Transcript start position
        'tx_end': 'txEnd',              # Transcript end position
        'cds_start': 'cdsStart',        # CDS start (including stop codon adjustment)
        'cds_end': 'cdsEnd',            # CDS end (including stop codon adjustment)
        'exon_starts': 'exonStarts',     # Comma-separated exon start positions
        'exon_ends': 'exonEnds'          # Comma-separated exon end positions
    })

    # Write output as tab-separated file
    joined_df.write_csv(output_file, separator='\t')

    return joined_df

# =============================================================================
# CDS Extraction and Quality Control Functions
# =============================================================================

def extract_cds_sequence(row, fasta):
    """
    Extract the coding sequence (CDS) for a transcript from the reference genome.
    
    This function:
    1. Iterates through exons and extracts only the CDS-overlapping portions
    2. Concatenates exon sequences in genomic order
    3. Reverse complements for minus strand genes
    
    Args:
        row: DataFrame row containing transcript annotation (chrom, strand, cdsStart, cdsEnd, exonStarts, exonEnds)
        fasta: Dictionary mapping chromosome names to their sequences
        
    Returns:
        str: The complete CDS sequence in 5' to 3' orientation (transcript strand)
    """
    chrom = row['chrom']
    strand = row['strand']
    cds_start = row['cdsStart']
    cds_end = row['cdsEnd']

    COMPLEMENT = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N'}
    
    # Parse comma-separated exon coordinates from annotation file
    exon_starts = [int(x) for x in row['exonStarts'].rstrip(',').split(',')]
    exon_ends = [int(x) for x in row['exonEnds'].rstrip(',').split(',')]

    # Ensure exon boundaries encompass the full CDS (handles edge cases)
    if exon_starts[0] > cds_start:
        exon_starts[0] = cds_start
    if exon_ends[-1] < cds_end:
        exon_ends[-1] = cds_end

    # Extract CDS sequence by iterating through exons
    cds_sequence = ""
    
    for start, end in zip(exon_starts, exon_ends):
        # Find overlap between this exon and the CDS region
        overlap_start = max(start, cds_start)
        overlap_end = min(end, cds_end)
        
        if overlap_start < overlap_end:
            # Extract sequence from this exon segment (0-based coordinates)
            seq = str(fasta[chrom][overlap_start:overlap_end]).upper()
            cds_sequence += seq
    
    # For minus strand genes, reverse complement to get 5' to 3' orientation
    if strand == '-':
        cds_sequence = ''.join(COMPLEMENT[base] for base in cds_sequence[::-1])
    
    return cds_sequence

def check_cds_quality(sequence):
    """
    Validate CDS sequence quality for downstream variant analysis.
    
    Quality criteria checked:
    1. Starts with ATG (methionine start codon)
    2. Ends with a stop codon (TAA, TAG, or TGA)
    3. Length is divisible by 3 (complete codons)
    4. No premature stop codons within the coding region
    
    Args:
        sequence: CDS nucleotide sequence string
        
    Returns:
        dict: Quality metrics including boolean flags and sequence length
    """
    if not sequence or len(sequence) < 3:
        return {
            'has_start_codon': False,
            'has_stop_codon': False,
            'length_divisible_by_3': False,
            'has_internal_stop_codons': False,
            'length': len(sequence) if sequence else 0
        }
    
    # Check for canonical start codon (ATG = Methionine)
    has_start_codon = sequence[:3] == 'ATG'
    
    # Check for stop codon at the end
    has_stop_codon = sequence[-3:] in ['TAA', 'TAG', 'TGA']
    
    # CDS should be in-frame (length divisible by 3)
    length_divisible_by_3 = len(sequence) % 3 == 0
    
    # Check for internal stop codons (premature termination)
    # These indicate potential annotation errors or pseudogenes
    has_internal_stop_codons = False
    if len(sequence) >= 6:  # Need at least 2 codons to check for internal stops
        # Check all codons except the last one (which should be a stop)
        for i in range(0, len(sequence) - 3, 3):
            codon = sequence[i:i+3]
            if codon in ['TAA', 'TAG', 'TGA']:
                has_internal_stop_codons = True
                break
    
    return {
        'has_start_codon': has_start_codon,
        'has_stop_codon': has_stop_codon,
        'length_divisible_by_3': length_divisible_by_3,
        'has_internal_stop_codons': has_internal_stop_codons,
        'length': len(sequence)
    }
