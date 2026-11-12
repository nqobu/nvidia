# Build a VISTA2D Workflow with Your Agent 透過代理建立 VISTA2D 流程

## Check GPU Resources

Run only one GPU course at a time on this workshop VM.

1. **Save and close the previous kernel.** Save the previous course's notebook, then shut down its kernel in **Running Terminals and Kernels** in that course's JupyterLab. Closing a browser tab does not release GPU memory.
2. **Check GPU use.** Open **File → New → Terminal** and run `bootcamp-resources status`.
3. **Prepare this course.** If any BioNeMo models are running, run `bootcamp-resources stop --confirm`.
4. **Confirm readiness.** Run `bootcamp-resources status` again. Continue only when the BioNeMo models are stopped and `gpu_processes` is empty.

For the complete instructions, see `00_START_HERE.txt` in the course root directory.

Your agent will write three useful scripts: model preparation, pretrained VISTA2D
inference, and visualization. The scripts are intentionally absent at the start.
You stay in the notebook to see code before and after generation, run it, and inspect
real microscopy results. You do not need to type Python yourself.

代理將撰寫三個實用腳本：模型準備、VISTA2D 預訓練推論與視覺化。起始教材刻意不提供這些檔案。
你在筆記本觀看生成前後程式、執行並觀察真實顯微影像結果，不需自行輸入 Python。

The VM image already contains the uv environment and official checkpoints. Use
`.venv/bin/python` and the interpreter configured in classroom.json; do not
create environments or install packages. Preparation in the notebook uses
`--check-only`, so class runs verify the shared cache without downloading.
Copy only one language section from each card. Complete English and Traditional
Chinese prompts are also available in prompts/en/ and prompts/zh-TW/.

VM 映像已備妥 uv 環境與官方權重，請使用 `.venv/bin/python` 與 classroom.json 的既有 Python，
不要建立環境或安裝套件。筆記本使用 `--check-only`，課堂只驗證共用快取而不下載。
每張提示卡只選一種語言貼給代理；完整英文與繁體中文版也位於 prompts/en/、prompts/zh-TW/。

## The notebook loop 筆記本操作循環

1. Run **Before the agent** to capture the current file, or its absence. 執行「代理執行前」，記錄目前檔案或尚未存在的狀態。
2. Paste your chosen English or Traditional Chinese request into your existing agent interface. 將選定的英文或繁體中文提示詞貼到既有代理介面。
3. Run **After the agent** to print the new code and a diff. 執行「代理執行後」，印出新程式與差異。
4. Run **Execute** and inspect the output or error in the notebook. 執行程式，在筆記本觀察結果或錯誤。
5. For a failure, share the error, request one focused repair, and view the new diff. 失敗時提供錯誤，要求一次針對性修正，再查看差異。

Keep the morning instructor's working harness. The language model cannot see images;
you make visual judgments. All commands run from the lesson root. The instructor has
staged VISTA source and installed dependencies. Follow docs/VISTA2D_API.md; do not call
finished workshop wrappers, copy staff solutions, train a model, or change dependencies.

沿用上午代理。語言模型不能看圖，視覺判斷由你負責。所有命令在教材根目錄執行，講師已放好 VISTA
原始碼並安裝相依套件。依介面說明實作，不呼叫現成教材包裝程式、不複製解答、不訓練或變更相依套件。

## Mission 1 Model preparation 任務一模型準備

**5–17 minutes / 第 5–17 分鐘**

Use [prompt 01](prompts/01_prepare.md) to create prepare_model.py. Review its code,
then run it from the notebook. It reads official download URLs and checksums from
assets.json. Cached weights are verified; missing weights are downloaded. A valid
SAM initialization file and a trained VISTA2D checkpoint are both required.

使用提示詞 01 建立 prepare_model.py，檢視程式後在筆記本執行。從資源清單取得官方網址與校驗碼，
驗證快取或下載缺少權重。需要 SAM 初始化與訓練完成的 VISTA2D 權重。

```bash
.venv/bin/python prepare_model.py --check-only
.venv/bin/python tools/check_mission.py prepare
```

## Mission 2 Inference 任務二推論

**17–33 minutes / 第 17–33 分鐘**

Use [prompt 02](prompts/02_infer.md) to create run_vista.py. It adapts the official
MONAI config and launches the pretrained model. Review the code, run a configuration-only
dry run, then execute GPU inference. Keep the raw mask, log, derived config, and run record.

使用提示詞 02 建立 run_vista.py，調整官方 MONAI 設定並啟動預訓練模型。先檢視程式、執行只產生設定
的 dry-run，再執行 GPU 推論，保留原始遮罩、紀錄、衍生設定與執行資訊。

```bash
.venv/bin/python run_vista.py --sample fluorescence --output outputs/fluorescence
.venv/bin/python tools/check_mission.py infer --output outputs/fluorescence
```

## Mission 3 Reveal the result 任務三展示結果

**33–45 minutes / 第 33–45 分鐘**

Use [prompt 03](prompts/03_second_image.md) to create visualize.py. Review its code,
then run it to draw predicted boundaries beside the original. The agent creates a
visualization of VISTA2D's real prediction; it does not create or repair the mask.

使用提示詞 03 建立 visualize.py，檢視後執行，將預測邊界與原圖並排。代理建立真正 VISTA2D 預測的
視覺化，不產生或修復遮罩。

```bash
.venv/bin/python visualize.py --image data/microscopy/img00.png --mask outputs/fluorescence/mask.tif --output outputs/fluorescence/comparison.png
.venv/bin/python tools/check_mission.py visualize --output outputs/fluorescence
```

## Explore and save 探索與儲存

**45–50 minutes / 第 45–50 分鐘**

Save the notebook with before/after code and one boundary observation. If time permits,
reuse your new scripts on Cellpose img02 with [prompt 04](prompts/04_optional_nuclei.md).
The grayscale and nuclei inputs are channel variants of that same image, not independent samples.

儲存含生成前後程式及邊界觀察的筆記本。有時間可依提示詞 04 沿用新程式處理 Cellpose img02。
灰階與細胞核輸入是同一影像的通道版本，不是獨立樣本。

An execution/output check does not prove segmentation accuracy. Ask: which boundaries
look convincing, and where might cells have merged, split, or been missed?

執行／輸出檢查不代表分割準確。請觀察哪些邊界可信，哪些可能合併、切碎或漏掉細胞。

## Recovery 遇到問題

Paste the notebook error or inference.log into the agent. Keep before/after views for
repairs too. Ask a teaching assistant after one focused repair. Choose a fresh output
directory if the prior one is nonempty. Do not blindly delete outputs. Staff may release
one checkpoint script; record that assistance and continue writing the next script.

將筆記本錯誤或 inference.log 提供給代理，修復也保留前後檢視。一次針對性修復後仍失敗請助教協助。
舊輸出非空時改用新目錄，不任意刪檔。講師可提供單一階段解答；記錄協助後繼續下一個程式生成任務。

## Save and Release GPU Resources

1. **Save and shut down.** Save this notebook, then shut down its kernel in **Running Terminals and Kernels**.
2. **Release resources.** In **File → New → Terminal**, run `bootcamp-resources status` to check that this course has released the GPU.
3. **Check before switching.** Run `bootcamp-resources status` and confirm that `gpu_processes` is empty before opening the next course's kernel.

When returning to BioNeMo, follow **Check GPU Resources** at the beginning of its lesson and wait for all three models to become **healthy**.
