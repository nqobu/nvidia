# VISTA2D Coding Brief VISTA2D 程式實作說明

Create three small standalone scripts at the lesson root. This brief supplies
interfaces, not complete implementations. Use the standard library and Pillow
for preparation/visualization; the prepared model environment supplies MONAI.
Do not import workshop helpers or copy instructor solutions.

在教材根目錄建立三個小型獨立腳本。本說明提供介面，不提供完整實作。準備與視覺化使用標準
函式庫及 Pillow，MONAI 由已備妥的模型環境提供。不匯入 workshop 工具或複製講師解答。

## Existing environment and cache 既有環境與快取

Use the instructor-prepared uv environment. Run checks with `.venv/bin/python`;
use classroom.json's configured absolute model interpreter for MONAI. Do not
create environments, run `uv venv`, or install/upgrade packages or drivers.
The VM image contains both official checkpoints under models/. Mission 1 still
implements download support, but the normal notebook uses `--check-only` to
verify the cache without downloading. Preserve valid cached files.

沿用講師準備的 uv 環境，以 `.venv/bin/python` 執行檢查；MONAI 使用 classroom.json 中
既有的絕對模型 Python 路徑。不要建立環境、執行 `uv venv`、安裝／升級套件或驅動。
VM 映像已在 models/ 預放兩個官方權重。任務一仍需實作下載功能，但筆記本正常流程使用
`--check-only` 驗證快取而不下載。請保留有效快取。

## Shared files 共用檔案

- assets.json: checkpoints contains name, path, url, md5. Paths are relative to
  the lesson root. 內含權重名稱、相對路徑、網址與 MD5。
- classroom.json: vista2d contains bundle, sam_checkpoint, model_checkpoint,
  python; images maps sample names to real images. 內含 bundle、權重、Python 與影像對照。
- vendor/VISTA/vista2d/configs/inference.json: official config staged by the
  instructor. 講師已放好的官方推論設定。
- support/save_mask.py: supplied output writer only. It does not download,
  configure, run, or visualize a model. 僅提供輸出儲存器，不包含下載、設定、執行或視覺化流程。

Resolve paths using the directory of the created script, not a notebook's
current folder. Each script must have a main guard so importing it has no side effects.

以腳本所在目錄解析路徑，不依賴筆記本目前目錄。每個腳本使用 main guard，避免匯入時執行操作。

## prepare_model.py

CLI / 命令列: `python3 prepare_model.py [--check-only]`

Read assets.json checkpoints. For each file, compute its MD5 in chunks. Reuse a
matching file. Preserve and report a mismatching existing file. For a missing
file, download from its supplied URL to a temporary .part file, verify MD5, then
rename to the final path. With --check-only, missing files cause failure without
network access. Exit nonzero on failure and clean up partial downloads.

讀取權重清單，分段計算 MD5。符合則沿用；既有檔不符時保留並回報錯誤。缺少時從指定網址下載至
.part，驗證後改名。--check-only 不連網，遇到缺漏則失敗。錯誤時回傳非零狀態並清除未完成下載。

Write preparation.json only after every checkpoint is verified. Include a
checkpoints array with path and status (`downloaded` or `verified`). A cached file
must not be described as newly downloaded. Do not install packages or clone source.

全部權重驗證後才寫入 preparation.json，內含 checkpoints 列表與 path、status。
快取不得稱為新下載。不安裝套件或複製原始碼。

## run_vista.py

CLI / 命令列:
`python3 run_vista.py --sample fluorescence --output outputs/fluorescence [--dry-run]`

Read classroom.json. Load the upstream inference JSON and write a new config in
the output directory. Require an empty/new output directory. Set these entries:

讀取 classroom.json，載入上游 JSON，將新設定寫入新建或空的輸出目錄。指定下列項目：

| Config key 設定 | Value 值 |
| --- | --- |
| bundle_root | Absolute VISTA2D bundle directory 絕對 bundle 路徑 |
| input_dict | A dictionary with image set to the absolute input path 影像絕對路徑字典 |
| sam_ckpt_path | Absolute SAM checkpoint path SAM 權重絕對路徑 |
| pretrained_ckpt_path | Absolute VISTA2D checkpoint path VISTA2D 權重絕對路徑 |
| device | Literal MONAI expression `$torch.device('cuda:0')` 原樣使用此表示式 |

Keep preprocessing, network, inferer, and instance decoder unchanged. Replace
only the final entry of postprocessing.transforms with a transform specification:
_target_ = support.save_mask.SaveInstanceMask; keys = pred; output_path = the
absolute output/mask.tif path. This narrow writer is provided because the raw
mask should be saved separately from its visualization.

保留前處理、網路、推論器及實例解碼器。只將 postprocessing.transforms 最後一項改為上述儲存器，
指定 pred 與輸出遮罩絕對路徑。此儲存器讓原始遮罩與視覺化分開保存。

Save the new JSON as vista_inference.json. Execute the model interpreter from
classroom.json with arguments `-m monai.bundle run --config_file ABSOLUTE_CONFIG`.
Use subprocess.run with a list of arguments and check=True, cwd=bundle. Prepend
the lesson root to the child process's PYTHONPATH so it can import support.
Capture stdout and stderr together in inference.log. Require CUDA before inference.

新 JSON 命名為 vista_inference.json。使用設定中的模型 Python 與上述參數，透過參數列表執行，
指定 check=True、cwd=bundle。將教材根目錄加到子程序 PYTHONPATH，讓模型可匯入 support。
標準輸出與錯誤合併存至 inference.log；真正推論前需確認 CUDA。

On successful model execution and mask creation, write run.json with source =
vista2d_inference, input_image (absolute path), model_checkpoint, command (list),
and elapsed_workflow_seconds. Time includes startup and checkpoint loading.
--dry-run writes the config and displays the command, runs no child process, and
does not write run.json or a mask. Never turn a failed run into a success record.

模型成功且遮罩存在後，寫入含上述欄位的 run.json。耗時包含啟動與權重載入。
--dry-run 只寫設定及顯示命令，不執行子程序，也不寫入 run.json 或遮罩。失敗不可記為成功。

## visualize.py

CLI / 命令列:
`python3 visualize.py --image INPUT.png --mask MASK.tif --output comparison.png`

Use Pillow. Preserve the original mask and integer label IDs. Validate a
single-frame 2D integer mask with nonnegative IDs and the same size as the input.
Convert only the display input to RGB. Background is 0; identify boundaries where
a foreground pixel touches a different label or an image edge. Draw bright,
deterministic label colors on a copy of the input. Save a side-by-side original
and overlay PNG with short English captions. The canvas width must equal twice
the input width, with no horizontal gutter; extra height for captions is allowed.
Never use the background's black color for a positive label. Do not resize either panel.

使用 Pillow，保留原遮罩與整數標籤。驗證遮罩為單張二維非負整數，且與輸入尺寸一致。
只將顯示用輸入轉為 RGB。0 為背景；前景與不同標籤相鄰或位於影像邊緣時視為邊界。
以固定且明亮的標籤顏色畫在輸入副本上，將原圖與疊圖並排儲存 PNG，附簡短英文標題，不縮放。
畫布寬度恰為輸入寬度兩倍，中間不留水平空隙；可增加標題區域高度。正標籤不可使用背景黑色。

Pillow image.get_flattened_data() returns pixel values in row-major order in the
pinned lesson version. image.load() gives access as pixels[x, y]. Do not count
max(label) as the number of objects. You need no area measurements or classifier.

教材固定版本的上述 Pillow 方法可讀取像素；image.load() 使用 pixels[x, y] 存取。
最大標籤不是物件數，不需實作面積量測或分類器。

## Sources 來源

These interfaces use the pinned [VISTA2D inference config](https://github.com/Project-MONAI/VISTA/blob/d4a8fe0dbf5cb4b76c531fccca8e29c1e6f6ee45/vista2d/configs/inference.json).
The [original tutorial](https://github.com/Project-MONAI/tutorials/tree/main/vista_2d)
includes training; this lesson loads published VISTA2D weights for inference.

以上依固定版本設定整理；原教學包含訓練，本課程載入發布權重進行推論。
