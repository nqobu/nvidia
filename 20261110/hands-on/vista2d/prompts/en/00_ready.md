# Environment check

Read WORKSHOP.md. Report the configured model interpreter in classroom.json and
whether the staged upstream inference config exists. Do not read instructor/checkpoints
or finished workshop wrappers. Do not install packages. I will use the notebook for GPU checks.

Reply in English.

Work from the lesson root and use the existing uv-managed environment. Use
`.venv/bin/python` for Python syntax checks and `--help`. For the model subprocess,
use the absolute interpreter already configured in `classroom.json`. Do not create
an environment, run `uv venv`, install or upgrade packages, or change GPU drivers.
The official checkpoints are pre-cached under `models/` in this VM image: verify
and reuse them. Never delete or force a re-download of valid cached weights.
