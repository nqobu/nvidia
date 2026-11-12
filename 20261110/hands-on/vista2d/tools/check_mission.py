"""Check mission outputs without implementing download, inference, or visualization."""
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]


def check(mission, output=Path("outputs/fluorescence")):
    if mission == "prepare":
        for filename in ["prepare_model.py", "preparation.json"]:
            if not (ROOT / filename).is_file():
                raise ValueError(f"Missing / 缺少: {filename}")
        entries = json.loads((ROOT / "assets.json").read_text())["checkpoints"]
        records = json.loads((ROOT / "preparation.json").read_text())["checkpoints"]
        if (len(records) != len(entries) or {record["path"] for record in records} != {entry["path"] for entry in entries}
                or any(record["status"] not in {"downloaded", "verified"} for record in records)):
            raise ValueError("Preparation record does not match verified assets / 準備紀錄與資源不符")
        for entry in entries:
            path = ROOT / entry["path"]
            checksum = hashlib.md5()
            with path.open("rb") as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                    checksum.update(chunk)
            if checksum.hexdigest() != entry["md5"]:
                raise ValueError(f"Checkpoint hash mismatch / 權重校驗失敗: {path}")
    else:
        output = ROOT / output
        record = json.loads((output / "run.json").read_text())
        if record.get("source") != "vista2d_inference":
            raise ValueError("Expected an actual VISTA2D run record / 需要真正推論紀錄")
        with Image.open(record["input_image"]) as image, Image.open(output / "mask.tif") as mask:
            if (image.size != mask.size or getattr(mask, "n_frames", 1) != 1 or
                    mask.mode not in {"L", "I", "I;16", "I;16L", "I;16B"} or
                    any(v < 0 for v in mask.get_flattened_data())):
                raise ValueError("Mask needs matching dimensions and integer label IDs / 遮罩尺寸或標籤不符")
            size = image.size
        if not (ROOT / "run_vista.py").is_file() or not (output / "inference.log").is_file():
            raise ValueError("Inference script or log is missing / 缺少推論程式或紀錄")
        if mission == "visualize":
            if not (ROOT / "visualize.py").is_file():
                raise ValueError("Missing visualize.py / 缺少視覺化程式")
            with Image.open(output / "comparison.png") as comparison:
                if comparison.format != "PNG" or comparison.width != size[0] * 2 or comparison.height < size[1]:
                    raise ValueError("Expected unscaled side-by-side PNG / 需要原尺寸並排 PNG")
    return {"mission": mission, "status": "passed", "scope": "file and data checks; not biological accuracy or proof of authorship"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mission", choices=["prepare", "infer", "visualize"])
    parser.add_argument("--output", type=Path, default=Path("outputs/fluorescence"))
    args = parser.parse_args()
    try:
        print(json.dumps(check(args.mission, args.output), indent=2))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"Check failed / 檢查失敗: {error}\n")


if __name__ == "__main__":
    main()
