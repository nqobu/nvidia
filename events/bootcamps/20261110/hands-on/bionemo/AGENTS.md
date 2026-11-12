# Rebuilding outside the classroom

First read ../AGENTS.md and this folder's README.md. During initial setup in a NEW
environment you may create the documented virtualenv, install the pinned packages,
fetch sources and cache assets. Once ready, follow the lesson rules below; their
no-install instructions apply to the lesson phase. Never alter a running classroom VM.

# EGFR virtual screening

Use the learner's configured agent and model provider (NCHC RAP when available). Load the installed
official BioNeMo Agent Toolkit skills: drug-discovery-pipeline, genmol-nim,
diffdock-nim, and boltz2-nim. Follow BioNeMo_with_Agent.md and work only on the requested step.

Use EGFR chain A and gefitinib (IRE) from PDB 2ITY. Retrieve public inputs when
requested; use the supplied genuine EGFR alignment for Boltz-2. Read API request
examples in BioNeMo_Workflow.ipynb. Use support/workshop.py for the shared request
cache, candidate submission guard, and predefined viewer.

## File Organization

Keep the course root (this `bionemo/` directory) clean. It is the main directory
visible in JupyterLab. Do not create task scripts, helper modules, temporary
files, or additional notebooks in this directory.

- Put task-specific generated code in `results/agent/scripts/`.
- Put reusable generated helpers in `support/agent/`, separate from the supplied
  support files. Reuse existing utilities before creating new helpers.
- Save run data and reports in `results/agent/` and visualizations in
  `figures/agent/`.
- Resolve input and output paths against `support.workshop.ROOT`. When a script
  is moved, update its imports, execution commands, and file references.

## Implementation settings

Start with the NVIDIA Build Deploy examples for
[GenMol](https://build.nvidia.com/nvidia/genmol-generate/deploy),
[DiffDock](https://build.nvidia.com/mit/diffdock/deploy), and
[Boltz-2](https://build.nvidia.com/mit/boltz2/deploy).
Use their linked API documentation for the deployed image versions when examples differ.
Keep request dictionaries and requests.post calls simple and explicit. Do not invent
SAFE encodings, add automatic retries, or add speculative exception handlers.
Retain the requested invalid-molecule filtering and single-candidate submission guard.

Resolve the lesson's plain-language requests using these defaults. Keep helper
names and request syntax out of explanations unless specifically requested.

- Inputs: retrieve `https://files.rcsb.org/download/2ITY.pdb` and
  `https://files.rcsb.org/ligands/download/IRE_ideal.sdf`. Follow the notebook's
  extraction of EGFR chain A, complete SEQRES sequence, and experimental IRE
  coordinates with restored bond orders. Save inputs under `results/agent/inputs/`.
- GenMol: use `support.workshop.GENMOL_TEMPLATE`, `num_molecules=20`,
  `temperature=1.0`, `noise=1.0`, `min_add_len=24`, `scoring='QED'`,
  `unique=True`, and `filter=False`. Use `curate(..., limit=3)` for local
  validation. Pass the complete core SMILES without an explicit mask or manual SAFE conversion.
  Save the curation report with each returned molecule marked invalid, excluded,
  or selected and its reason. Continue with one or two eligible molecules. If none
  remain, report that and skip downstream calls without raising a selection error.
  Do not automatically issue additional requests.
- DiffDock: dock gefitinib and the eligible shortlist with `ligand_file_type='txt'`,
  `num_poses=5`, `time_divisions=20`, `steps=18`, `save_trajectory=False`.
  Select the analogue with the highest top-pose confidence. Save its candidate ID
  and canonical SMILES in `results/agent/chosen_candidate.json`.
- Boltz-2: use `boltz_payload` with the complete matching sequence and
  `data/egfr.a3m`. Submit through `call_nim('boltz2', payload, results_directory,
  candidate=True)`, with `results_directory` set to `results/agent/`.
  Load the reference using `load_reference(payload)` and its `gefitinib` entry.
- Artifacts: use `call_nim` for full request/response envelopes and caching.
  Save SDF docking poses, the Boltz-2 mmCIF, and a CSV affinity comparison under
  `results/agent/`. Use `align_boltz_ligand` before the predefined `show_complex`
  view; save molecule grids and complex images under `figures/agent/`.

The initial setup prompt explicitly authorizes installing the four official
Toolkit skill directories into ~/.config/opencode/skills/ and cloning its source
into ~/.local/share/bionemo-agent-toolkit. Complete that setup before loading skills.

Follow the file locations above for generated code and results. Use local NIM endpoints
from support.workshop.ENDPOINTS. Do not deploy containers, install packages, change
system configuration, or edit the supplied notebook/support code during
the lesson. The course does not mount the Docker socket.

Run Boltz-2 live for ONLY ONE generated candidate using call_nim(..., candidate=True).
Read gefitinib from data/reference_results.json. Never bypass the submission guard
or delete its ledger to retry. Explanation requests use existing results and make
no new model calls. Keep the returned molecule identity with every score and pose.

Prepared results are an explicit user choice. If requested, load prepared/
and identify the prepared candidate by its actual SMILES/ID. Do not present a
prepared candidate's scores as scores for a different live-generated molecule.
Never introduce automatic timing or automatic switching.

Use the predefined py3Dmol style: grey protein cartoon, green reference ligand
wireframe, orange candidate sticks. Align the Boltz-2 complex to experimental
EGFR before overlaying it. Save images under figures/agent/, leaving the fixed
representative figures under figures/ unchanged.
