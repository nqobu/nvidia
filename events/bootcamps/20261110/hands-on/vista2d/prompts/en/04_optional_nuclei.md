# Optional Reuse your new scripts

Using the scripts you created, tell me the notebook commands for a second run with
--sample cellpose_demo and --output outputs/cellpose-demo, followed by visualization.
Do not retrain or rewrite the model. After that, optionally use the nuclei sample and
ask whether our intended target is a nucleus or a whole cell. Do not launch these runs
until I execute the notebook cell. Do not judge accuracy without labeled comparisons.

Reply in English.

Work from the lesson root and use the existing uv-managed environment. Use
`.venv/bin/python` for Python syntax checks and `--help`. For the model subprocess,
use the absolute interpreter already configured in `classroom.json`. Do not create
an environment, run `uv venv`, install or upgrade packages, or change GPU drivers.
The official checkpoints are pre-cached under `models/` in this VM image: verify
and reuse them. Never delete or force a re-download of valid cached weights.
