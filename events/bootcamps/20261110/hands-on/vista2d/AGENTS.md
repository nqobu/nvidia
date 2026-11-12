# Rebuilding outside the classroom

First read ../AGENTS.md and this folder's README.md. During initial setup in a NEW
environment you may create the documented virtualenv, install the pinned packages,
fetch sources and cache assets. Once ready, follow the lesson rules below; their
no-install instructions apply to the lesson phase. Never alter a running classroom VM.

# VISTA2D lesson agent guidance

Read WORKSHOP.md before acting. Student-facing instructions are bilingual English
and Traditional Chinese. The central activity is preparing and running VISTA2D
on real microscopy images. No synthetic classroom data or coding puzzles.

- Continue with the student's existing harness. Do not install another harness.
- Use commands from the project root and the configured Python interpreter.
- Create prepare_model.py, run_vista.py, and visualize.py from the mission briefs.
- Read docs/VISTA2D_API.md for exact interfaces. Do not wrap or copy a finished lesson helper.
- Mission 1 writes checkpoint download/cache code; source and dependencies are staged by instructors.
- Use the existing uv environment: .venv/bin/python for checks and the configured
  absolute interpreter in classroom.json for MONAI. Do not create an environment,
  run uv venv, or install/upgrade dependencies or GPU drivers.
- Official weights are pre-cached in models/ on the VM image. Normal notebook
  preparation uses --check-only. Implement downloads for missing files, but do
  not delete valid weights or force downloads to demonstrate the code.
- Paste only one language section from a prompt card; prompts/en/ and
  prompts/zh-TW/ contain complete single-language versions.
- Keep images, model source, and validation code intact. Download missing weights but do not alter valid cached weights.
- Do not fabricate masks or substitute a different segmentation model.
- Report checkpoint paths, actual execution, elapsed time, and saved outputs.
- After failure read inference.log. Try one focused path/config repair, then ask for help.
- The language model does not view images. Ask the student to inspect the result.
- A cached file or saved prediction is not a new inference run. Describe it accurately.
- Core code generation is for VISTA2D preparation, inference, and visualization.
- Do not read instructor/checkpoints/, workshop/, or tools/run_segmentation.py to solve a student mission.
- These files are instructor references and are excluded from the student bundle.
