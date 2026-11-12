# Mission 1 Write the model preparation script

Read WORKSHOP.md, docs/VISTA2D_API.md, and the checkpoints entries in assets.json.
Create prepare_model.py implementing that brief using Python's standard library.
It must download missing checkpoints, verify MD5, reuse valid cached files, preserve
mismatching existing files, support --check-only, and write preparation.json after success.
Do not call a finished workshop helper or copy instructor code. Do not install packages.
Run a syntax check and --help, then stop so I can inspect the code and run it in the notebook.

Reply in English.

Work from the lesson root and use the existing uv-managed environment. Use
`.venv/bin/python` for Python syntax checks and `--help`. For the model subprocess,
use the absolute interpreter already configured in `classroom.json`. Do not create
an environment, run `uv venv`, install or upgrade packages, or change GPU drivers.
The official checkpoints are pre-cached under `models/` in this VM image: verify
and reuse them. Never delete or force a re-download of valid cached weights.

Implement the missing-file download path, but do not download or execute preparation yourself. The notebook will use `prepare_model.py --check-only` to verify the pre-cached weights. Stop after syntax checking and `--help`.
