#!/usr/bin/env bash
set -euo pipefail

# Run only on your own GPU VM host, or adapt to your cluster's approved runtime.
TASK_DATA_DIR=$(realpath "${1:?Provide the writable DATA_DIR}")
TASK_GPU_ID=${PARABRICKS_GPU_ID:-0}
TASK_IMAGE=nvcr.io/nvidia/clara/clara-parabricks:4.6.0-1@sha256:d0761eb4b9921bc046c53520287316d545eb79feaeb8f22387e9bb5734650447
for file in sample_1.fq.gz sample_2.fq.gz ref/Homo_sapiens_assembly38.fasta; do
  test -s "$TASK_DATA_DIR/$file" || { printf 'Missing input: %s\n' "$file" >&2; exit 1; }
done
mkdir -p "$TASK_DATA_DIR/out"
if [[ -e "$TASK_DATA_DIR/out/deepvariant.vcf.gz" || -e "$TASK_DATA_DIR/out/sample.bam" ]]; then
  printf 'Existing output preserved. Use a new DATA_DIR for a new run; inspect existing results before reusing them.\n' >&2
  exit 1
fi
docker run --rm --gpus "device=$TASK_GPU_ID" \
  --mount "type=bind,source=$TASK_DATA_DIR,target=/workdir" --workdir /workdir \
  "$TASK_IMAGE" pbrun deepvariant_germline \
  --ref ref/Homo_sapiens_assembly38.fasta \
  --in-fq sample_1.fq.gz sample_2.fq.gz \
  --out-variants out/deepvariant.vcf.gz --out-bam out/sample.bam
