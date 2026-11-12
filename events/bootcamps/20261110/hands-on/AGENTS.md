# Environment setup for the public teaching materials

Read README.md, environment.json, and the selected course's README.md first.
The per-course lesson instructions apply AFTER setup. Initial setup in a new,
user-owned environment may install documented packages, download sources/assets,
and create isolated virtualenvs or containers. Do not change a live classroom VM.

- Keep BioNeMo, VISTA2D, RAPIDS Single-cell and PyTorch Genomics separate.
- Use the pinned image/source references and existing scientific helper files.
- On a cluster honor the allocated GPU devices, scheduler, scratch space, runtime
  and port-forwarding policy. Do not assume sudo, Docker or a public notebook port.
- Use a personal NGC key for NIM access and the user's own model-provider account
  for an agent. Never read another user's credentials or publish local secrets.
- The original classroom `bootcamp-resources` CLI is optional. Outside class use
  the selected course's documented commands and your own model services.
- Do not replace real datasets, checkpoints or scientific calculations with mocks.
- VISTA2D's prepare_model.py, run_vista.py and visualize.py are learning tasks;
  do not generate them merely to configure the environment unless requested.
- Check package imports, CUDA availability, source/checkpoint hashes, kernels and
  notebook file saving. Describe checks actually run and any checks still pending.
- Stop after setup unless the learner requests analysis. Inference and data
  downloads can be substantial; preserve existing valid caches and outputs.
- Keep generated files in each course's documented results/output directories.
