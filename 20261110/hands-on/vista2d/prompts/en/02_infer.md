# Mission 2 Write a VISTA2D runner

Read docs/VISTA2D_API.md and vendor/VISTA/vista2d/configs/inference.json.
Create run_vista.py with --sample, --output, and --dry-run as specified in the brief.
Write a derived MONAI config, preserving preprocessing, network, inferer, and decoding.
Use the supplied support.save_mask.SaveInstanceMask only for saving the integer mask.
Execute the configured model Python through subprocess, preserve a log, and write run.json
only after actual successful inference. Do not train, change upstream source, import
workshop wrappers, or fabricate a mask. Syntax-check the file and test --help. Stop before
GPU execution: I will inspect the code and run its dry run and inference from the notebook.

Reply in English.

Work from the lesson root and use the existing uv-managed environment. Use
`.venv/bin/python` for Python syntax checks and `--help`. For the model subprocess,
use the absolute interpreter already configured in `classroom.json`. Do not create
an environment, run `uv venv`, install or upgrade packages, or change GPU drivers.
The official checkpoints are pre-cached under `models/` in this VM image: verify
and reuse them. Never delete or force a re-download of valid cached weights.

Do not execute `--dry-run` or real inference yourself, and do not create trial output directories. Test only syntax and `--help`; I will run both dry-run and inference in the notebook.
