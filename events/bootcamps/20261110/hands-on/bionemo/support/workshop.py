"""Small shared utilities for the course; model request bodies stay visible in the notebook."""
from pathlib import Path
import base64
import hashlib
import io
import json
import os

ROOT = Path(os.environ.get("WORKSHOP_ROOT", Path(__file__).resolve().parents[1]))
ENDPOINTS = {
    "genmol": os.environ.get("GENMOL_URL", "http://127.0.0.1:8001/generate"),
    "diffdock": os.environ.get("DIFFDOCK_URL", "http://127.0.0.1:8002/molecular-docking/diffdock/generate"),
    "boltz2": os.environ.get("BOLTZ2_URL", "http://127.0.0.1:8003/biology/mit/boltz2/predict"),
}
CORE = "COc1cc2ncnc(Nc3ccc(F)c(Cl)c3)c2cc1O"
# GenMol 2 accepts complete SMILES without an explicit mask. Let the NIM prepare
# its model input; partial SAFE with unmatched ring labels fails its input validator.
GENMOL_TEMPLATE = CORE
BOLTZ_SETTINGS = dict(recycling_steps=3, sampling_steps=50, diffusion_samples=1,
                      sampling_steps_affinity=50, diffusion_samples_affinity=1,
                      output_format="mmcif")


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def call_nim(stage, payload, directory, *, candidate=False):
    """Reuse identical results; never retry a submitted candidate affinity call automatically."""
    import requests
    directory = Path(directory)
    identity = {"url": ENDPOINTS[stage], "request": payload,
                "image": os.environ.get(stage.upper() + "_IMAGE", "unrecorded")}
    key = fingerprint(identity)
    path = directory / "requests" / f"{stage}_{key[:16]}.json"
    if path.exists():
        return read_json(path)
    if candidate:
        ledger = directory / "boltz2_candidate_submission.json"
        ledger.parent.mkdir(parents=True, exist_ok=True)
        try:
            with ledger.open("x", encoding="utf-8") as handle:
                json.dump(identity, handle, indent=2)
        except FileExistsError:
            raise RuntimeError("A candidate Boltz-2 request has already been submitted in this run. Reuse its result or choose prepared results.") from None
    response = requests.post(
        ENDPOINTS[stage],
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        json=payload,
        timeout=(15, 1800),
    )
    response.raise_for_status()
    envelope = dict(identity, response=response.json())
    save_json(path, envelope)
    return envelope


def molecule(smiles):
    from rdkit import Chem
    from rdkit.Chem import Descriptors, Crippen, QED
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError("Invalid SMILES")
    smiles = Chem.MolToSmiles(mol)
    return dict(candidate_id="mol_" + hashlib.sha256(smiles.encode()).hexdigest()[:10],
                smiles=smiles, MW=Descriptors.MolWt(mol), cLogP=Crippen.MolLogP(mol), QED=QED.qed(mol))


def curate(response, reference_smiles, limit=3, report_path=None):
    """Report rejected molecules and return up to limit eligible unique candidates."""
    from rdkit import Chem
    if response.get("status") != "success":
        raise ValueError("GenMol did not return a successful generation response.")
    core, rows, report = Chem.MolFromSmiles(CORE), {}, []
    reference_smiles = molecule(reference_smiles)["smiles"]
    for index, item in enumerate(response.get("molecules", []), start=1):
        smiles = item.get("smiles") if isinstance(item, dict) else None
        entry = dict(returned_index=index, smiles=smiles, valid_molecule=False,
                     status="invalid", reason="Invalid or empty SMILES")
        try:
            if not isinstance(smiles, str) or not smiles.strip():
                raise ValueError("Empty SMILES")
            row = molecule(smiles)
            mol = Chem.MolFromSmiles(row["smiles"])
            if any(atom.GetAtomicNum() == 0 for atom in mol.GetAtoms()):
                entry["reason"] = "Unfinished attachment atom"
                report.append(entry)
                continue
        except (ValueError, TypeError, RuntimeError):
            report.append(entry)
            continue
        entry.update(row, valid_molecule=True)
        reasons = []
        if len(Chem.GetMolFrags(mol)) != 1:
            reasons.append("Disconnected fragments")
        if row["smiles"] == reference_smiles:
            reasons.append("Same as gefitinib")
        if not 250 <= row["MW"] <= 550:
            reasons.append("MW outside 250–550")
        if not mol.HasSubstructMatch(core):
            reasons.append("Gefitinib-derived core not preserved")
        elif mol.GetNumHeavyAtoms() <= core.GetNumHeavyAtoms():
            reasons.append("Unchanged core")
        if row["smiles"] in rows:
            reasons.append("Duplicate molecule")
        if reasons:
            entry.update(status="excluded", reason="; ".join(reasons))
        else:
            rows[row["smiles"]] = row
            entry.update(status="eligible", reason="")
        report.append(entry)
    selected = sorted(rows.values(), key=lambda row: (-row["QED"], row["candidate_id"]))[:limit]
    selected_ids = {row["candidate_id"] for row in selected}
    for entry in report:
        if entry["status"] == "eligible":
            chosen = entry["candidate_id"] in selected_ids
            entry.update(status="selected" if chosen else "not shortlisted",
                         reason="" if chosen else f"Outside top {limit} by QED")
    if report_path is not None:
        save_json(report_path, report)
    return selected


def boltz_payload(smiles, sequence, msa):
    from Bio import SeqIO
    records = list(SeqIO.parse(io.StringIO(msa), "fasta"))
    query = "".join(c for c in str(records[0].seq) if c.isupper()) if records else ""
    if query != sequence or len(records) < 2:
        raise ValueError("Use the prepared genuine EGFR alignment with an exactly matching query sequence.")
    return {
        "polymers": [{
            "id": "A",
            "molecule_type": "protein",
            "sequence": sequence,
            "msa": {"msa_search": {"a3m": {
                "alignment": msa,
                "format": "a3m",
                "rank": 0,
            }}},
        }],
        "ligands": [{
            "id": "L1",
            "smiles": molecule(smiles)["smiles"],
            "predict_affinity": True,
        }],
        **BOLTZ_SETTINGS,
    }


def affinity(response, smiles):
    def first(value):
        return value[0] if isinstance(value, list) and value else value
    row = molecule(smiles)
    values = response["affinities"]["L1"]
    for name in ("affinity_pic50", "affinity_pred_value", "affinity_probability_binary"):
        row[name] = first(values.get(name))
    if all(row[name] is None for name in ("affinity_pic50", "affinity_pred_value", "affinity_probability_binary")):
        raise ValueError("Boltz-2 returned no affinity scores.")
    row["structural_confidence"] = first(response.get("confidence_scores"))
    return row


def context(payload):
    return {key: value for key, value in payload.items() if key != "ligands"}


def load_reference(payload):
    values = read_json(ROOT / "data/reference_results.json")
    reference = values["gefitinib"]
    expected = fingerprint(context(payload))
    if reference.get("input_hash") == expected:
        live_image = os.environ.get("BOLTZ2_IMAGE", "unrecorded")
        if reference.get("image", "unrecorded") != live_image:
            raise ValueError("Reference and live Boltz-2 image versions differ. Prepare a matching reference before class.")
        return values
    raise ValueError("The saved gefitinib reference does not match this EGFR alignment/settings. Prepare a matching reference before class.")


def align_boltz_ligand(response, smiles, receptor_pdb):
    """Align matching protein CA atoms and transform the predicted ligand with them."""
    from Bio.PDB import MMCIFParser, PDBParser, Superimposer
    from Bio.Align import PairwiseAligner
    from Bio.SeqUtils import seq1
    from rdkit import Chem
    raw = response["structures"][0]["structure"]
    parser = MMCIFParser(QUIET=True) if raw.lstrip().startswith("data_") else PDBParser(QUIET=True)
    mobile = parser.get_structure("prediction", io.StringIO(raw))
    fixed = PDBParser(QUIET=True).get_structure("reference", io.StringIO(receptor_pdb))
    def residues(structure):
        return [r for r in next(structure.get_models())["A"] if "CA" in r and r.id[0] == " "]
    a, b = residues(fixed), residues(mobile)
    aligner = PairwiseAligner(mode="global", match_score=2, mismatch_score=-1,
                             open_gap_score=-5, extend_gap_score=-0.5)
    alignment = aligner.align("".join(seq1(r.resname) for r in a), "".join(seq1(r.resname) for r in b))[0]
    left, right = [], []
    for (i, j), (k, l) in zip(*alignment.aligned):
        for ai, bi in zip(range(i, j), range(k, l)):
            if a[ai].resname == b[bi].resname:
                left.append(a[ai]["CA"])
                right.append(b[bi]["CA"])
    if len(left) < 100:
        raise ValueError("Insufficient matching EGFR residues for alignment.")
    fit = Superimposer()
    fit.set_atoms(left, right)
    fit.apply(list(mobile.get_atoms()))
    # Keep the submitted chemical graph. Proximity bonding from a PDB round trip
    # can invent bonds when predicted non-bonded atoms are close together.
    ligand_residues = [r for r in next(mobile.get_models()).get_residues()
                       if r.id[0] != " " and r.resname not in ("HOH", "WAT")]
    if len(ligand_residues) != 1:
        raise ValueError(f"Expected one predicted ligand residue; found {len(ligand_residues)}.")
    ligand = Chem.MolFromSmiles(smiles)
    if ligand is None or not ligand.GetNumAtoms():
        raise ValueError("The submitted ligand SMILES is invalid.")
    # The deployed Boltz-2 1.10 names atoms by element and the one-based
    # canonical rank of the H-complete input molecule. Validate the full mapping
    # before copying any coordinates; never guess an atom order from proximity.
    ranks = list(Chem.CanonicalRankAtoms(Chem.AddHs(ligand)))
    expected = {atom.GetSymbol().upper() + str(ranks[atom.GetIdx()] + 1): atom
                for atom in ligand.GetAtoms()}
    atoms = [atom for atom in ligand_residues[0].get_unpacked_list()
             if atom.element.upper() != "H"]
    actual = {atom.get_name(): atom for atom in atoms}
    if len(actual) != len(atoms) or set(actual) != set(expected):
        raise ValueError("Predicted atom identifiers do not match the submitted ligand for this NIM version.")
    conformer = Chem.Conformer(ligand.GetNumAtoms())
    for name, atom in expected.items():
        predicted = actual[name]
        if predicted.element.upper() != atom.GetSymbol().upper():
            raise ValueError("Predicted atom element does not match the submitted ligand.")
        conformer.SetAtomPosition(atom.GetIdx(), tuple(float(value) for value in predicted.coord))
    ligand.AddConformer(conformer)
    return Chem.MolToMolBlock(ligand), float(fit.rms)


def show_complex(receptor, reference_sdf, candidate_sdf=None, stem=None):
    """One viewer style; also save a standalone HTML and PNG for the Markdown lesson."""
    import py3Dmol
    from IPython.display import display, HTML
    library = base64.b64encode((ROOT / "support/3Dmol-min.js").read_bytes()).decode()
    viewer = py3Dmol.view(width=900, height=560, js="data:application/javascript;base64," + library)
    viewer.setBackgroundColor("white")
    viewer.addModel(receptor, "pdb")
    viewer.setStyle({"model": 0}, {"cartoon": {"color": "grey"}})
    viewer.addModel(reference_sdf, "sdf")
    viewer.setStyle({"model": 1}, {"line": {"color": "green", "linewidth": 2}})
    if candidate_sdf:
        viewer.addModel(candidate_sdf, "sdf")
        viewer.setStyle({"model": 2}, {"stick": {"color": "orange", "radius": 0.18}})
    viewer.zoomTo({"model": 1})
    viewer.zoom(0.8)
    html = viewer.write_html()
    if stem is not None:
        stem = Path(stem)
        stem.parent.mkdir(parents=True, exist_ok=True)
        stem.with_suffix(".html").write_text(html, encoding="utf-8")
        # Jupyter already has an asyncio loop; run synchronous browser capture in a worker.
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=1) as pool:
            pool.submit(_snapshot, html, viewer.uniqueid, stem.with_suffix(".png")).result()
    display(HTML(html))
    return viewer


def _snapshot(html, viewer_id, destination):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as runner:
        browser = runner.chromium.launch(executable_path="/usr/bin/chromium", headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--use-gl=angle",
                  "--use-angle=swiftshader", "--enable-unsafe-swiftshader"])
        try:
            page = browser.new_page(viewport={"width": 920, "height": 580})
            page.set_content(html)
            page.wait_for_function(f"window.viewer_{viewer_id} && window.viewer_{viewer_id}.getModel()")
            page.evaluate("async () => {await $3Dmolpromise; await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));}")
            page.locator('[id="3dmolviewer_' + viewer_id + '"]').screenshot(path=str(destination))
        finally:
            browser.close()
