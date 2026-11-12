# Mission 3 Write the result visualization

Read the visualize.py contract in docs/VISTA2D_API.md. Create visualize.py using Pillow.
Read the original image and the predicted integer TIFF mask, validate matching sizes,
and draw deterministic bright boundaries on a copy. Save the original and prediction
side by side as one comparison.png without resizing or changing the inputs. Provide
--image, --mask, and --output. Do not use a completed overlay helper or alter model results.
Syntax-check and test --help, then stop for notebook inspection and execution. You cannot
see the image: ask me to inspect the resulting comparison.

Reply in English.

Work from the lesson root and use the existing uv-managed environment. Use
`.venv/bin/python` for Python syntax checks and `--help`. For the model subprocess,
use the absolute interpreter already configured in `classroom.json`. Do not create
an environment, run `uv venv`, install or upgrade packages, or change GPU drivers.
The official checkpoints are pre-cached under `models/` in this VM image: verify
and reuse them. Never delete or force a re-download of valid cached weights.

Every positive label must use a bright color; never assign the black background color to a foreground boundary. The comparison canvas must be exactly twice the input width, without a horizontal gutter; an extra caption height is allowed.
