#!/usr/bin/env bash
set -euo pipefail

# Download the blueprint's public sample into a directory owned by the notebook user.
DATA_DIR=${1:?Provide a writable data directory}
mkdir -p "$DATA_DIR/ref" "$DATA_DIR/out" "$DATA_DIR/models"

ARCHIVE="$DATA_DIR/parabricks_sample.tar.gz"
if [[ ! -s "$DATA_DIR/sample_1.fq.gz" || ! -s "$DATA_DIR/sample_2.fq.gz" || ! -s "$DATA_DIR/ref/Homo_sapiens_assembly38.fasta" ]]; then
    wget --continue --progress=dot:giga -O "$ARCHIVE" \
        https://s3.amazonaws.com/parabricks.sample/parabricks_sample.tar.gz
    tar -xzf "$ARCHIVE" -C "$DATA_DIR"
    mv -f "$DATA_DIR"/parabricks_sample/Data/sample_* "$DATA_DIR"/
    mv -f "$DATA_DIR"/parabricks_sample/Ref/* "$DATA_DIR/ref"/
fi

printf 'Sample data ready in %s\n' "$DATA_DIR"
