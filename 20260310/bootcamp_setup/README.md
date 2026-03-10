# PhysicsNeMo AI-Powered Physics Bootcamp &mdash; 完整環境建置手冊

> [!NOTE]
> **閱讀說明**：本檔案為自給自足的操作手冊，所有指令與設定檔內容皆內嵌於此。在一臺全新的Linux VM（GPU：NVIDIA H200）上，依序執行各步驟即可完成環境建置。
>
> Base image使用官方`nvcr.io/nvidia/physicsnemo/physicsnemo`，託管於**NGC公開Catalog，可直接`docker pull`無需API Key或帳號登入**，與bootcamp官方Dockerfile一致。
>
> 教學素材來源：[AI-Powered-Physics-Bootcamp](https://github.com/openhackathons-org/AI-Powered-Physics-Bootcamp)

---

## 前置作業｜在NCHC雲平臺建立VM

> 平臺網址：<https://ai-cloud.iic.nchc.org.tw/>

### NCHC-1. 登入平臺

前往<https://ai-cloud.iic.nchc.org.tw/>登入，確認專案名稱為**NCHC-NVIDIA Joint Lab教育訓練**（專案ID：GOV114072）。

![NCHC登入後首頁](images/nchc-01-login.png)

### NCHC-2. 建立安全群組

在首頁（如NCHC-1截圖）服務區塊中，點擊「**安全群組**」，進入「安全群組管理」頁面，點擊「**+建立**」。

![安全群組管理頁面](images/nchc-02-security-group-mgmt.png)

進入「建立安全群組」頁面，「**名稱**」欄位保留預設值（例如：`sg1772642623211`），點擊「**下一步：規則設定>**」。

![建立安全群組&mdash;基本資訊](images/nchc-03-security-group-basic.png)

進入規則設定頁面，預設已有一條`egress ipv4`規則。點擊「**新增安全群組規則**」。

![安全群組規則設定](images/nchc-04-security-group-rules.png)

新增**SSH (port 22)**規則，欄位填寫如下：

| 欄位			| 填寫內容 |
| ----			| -------- |
| 方向			| `ingress` |
| 連接埠範圍（最小）	| `22` |
| 連接埠範圍（最大）	| `22` |
| 協定			| `tcp` |
| CIDR			| 填入當下用戶的IP（見下方說明） |

> [!TIP]
> **如何取得CIDR？**
> 1. 前往<https://www.whatismyip.com.tw/en/>查詢目前的公開IP（例如：`123.123.123.45`）
> 2. 若只允許單一IP連線：填入`123.123.123.45/32`
> 3. 若允許整個網段（例如辦公室IP範圍）：填入`123.123.123.0/24`

填寫完成後點擊「**確定**」。

![新增安全群組規則&mdash;SSH port 22](images/nchc-05-sg-rule-ssh.png)

規則新增完成後，清單中應出現`egress`與`ingress port 22`兩條規則。確認後點擊「**下一步：檢閱+建立>**」。

![安全群組規則清單](images/nchc-06-sg-rule-added.png)

確認名稱與規則(egress + ingress port 22)無誤後，點擊左下角「**建立**」。

![建立安全群組&mdash;確認並建立](images/nchc-07-sg-review.png)

安全群組建立完成。

### NCHC-3. 進入虛擬機器管理頁面

在左側選單點擊**虛擬機器**&rarr;**虛擬機器管理**，進入管理頁面後點擊「**+建立**」。

![虛擬機器管理頁面](images/nchc-08-vm-create.png)

### NCHC-4. 基本設定

進入「建立虛擬機器」頁面，共分六步驟：**基本設定**&rarr;**硬體設定**&rarr;**虛擬網路**&rarr;**儲存資訊**&rarr;**認證**&rarr;**初始化指令**。

** 基本設定**欄位填寫如下：

| 欄位		| 填寫內容 |
| ----		| -------- |
| 名稱		| 自訂（例如：`vm1772640765`） |
| 描述		| （選填） |
| 映像檔來源	| 點擊「**選擇**」&rarr;選擇**Ubuntu** |
| 映像檔標籤	| **24.04** |

填寫完成後，確認如圖所示，點擊「**下一步：硬體設定>**」。

![基本設定完成](images/nchc-09-vm-basic-complete.png)

### NCHC-5. 硬體設定

選擇型號**`GPU.small`**，點擊「**下一步：虛擬網路>**」。

| 型號		        | GPU型號	| GPU (張)	| CPU (Cores)	| 記憶體 (GiB)	| 開機磁碟 (GiB) |
| ----		        | :-----:	| :------:	| :---------:	| :----------:	| :------------: |
| GPU.large		| H200		| 2		| 192		| 1024		| 120 |
| **GPU.small**&#x2705;	| **H200**	| **1**		| **96**	| **512**	| **120** |
| CPU.medium		| -		| 0		| 16		| 32		| 120 |

> **為何選GPU.small？**
> PhysicsNeMo需要NVIDIA H200 GPU（建議 &ge;20 GB VRAM）、&ge;32 GB RAM、Ubuntu 22.04+、可連外網路。GPU.small提供H200&times;1、512 GiB RAM、Ubuntu 24.04，完全符合需求。

![硬體設定&mdash;選擇GPU.small](images/nchc-10-vm-hardware.png)

### NCHC-6. 虛擬網路設定

進入「虛擬網路」步驟，清單顯示`No data available`，需至少新增一張虛擬網卡。點擊「**新增虛擬網卡**」。

![虛擬網路設定](images/nchc-11-vm-network.png)

在「新增虛擬網卡」對話框中填寫：

| 欄位	        | 填寫內容 |
| ----	        | -------- |
| 虛擬網路	| `bootcamp` |
| 安全群組	| 選擇剛才建立的安全群組（例如：`sg1772643505388`） |

填寫完成後點擊「**確定**」。

![新增虛擬網卡](images/nchc-12-vm-nic.png)

確認清單出現`bootcamp`網路及對應安全群組後，點擊「**下一步：儲存資訊>**」。

![虛擬網路設定完成](images/nchc-13-vm-network-done.png)

### NCHC-7. 儲存資訊（建立虛擬磁碟）

進入「儲存資訊」步驟，點擊「**建立虛擬磁碟**」。

![儲存資訊](images/nchc-14-vm-storage.png)

在「建立虛擬磁碟」對話框中填寫：

| 欄位		| 填寫內容 |
| ----		| -------- |
| 名稱		| 保留預設（例如：`vol1772681329`） |
| 描述		| （選填） |
| 容量 (GiB)	| **100** |
| 類型		| `SSD` |

填寫完成後點擊「**確定**」。

![建立虛擬磁碟](images/nchc-15-vm-disk.png)

確認清單出現磁碟名稱與容量(100 GiB)後，點擊「**下一步：認證>**」。

![儲存資訊完成](images/nchc-16-vm-storage-done.png)

### NCHC-8. 認證設定

進入「認證」步驟：

| 欄位		| 填寫內容 |
| ----		| -------- |
| 鑰匙對認證	| **停用** |
| 密碼		| `NCHCbootcamp2026_` |

> [!IMPORTANT]
> **請務必記住此密碼**，後續SSH連線至VM時會需要輸入。

密碼設定完成後，點擊「**下一步：初始化指令>**」。

![認證設定](images/nchc-17-vm-auth.png)

### NCHC-9. 初始化指令

「初始化指令」欄位保留空白，直接點擊「**下一步：檢閱+建立>**」。

![初始化指令（略過）](images/nchc-18-vm-init.png)

### NCHC-10. 檢閱並建立VM

進入最後的「**檢閱+建立**」步驟，確認以下設定無誤：

| 項目	        | 確認內容 |
| ----	        | -------- |
| 名稱	        | `vm...`（自動產生） |
| 映像檔來源	| `Ubuntu` |
| 映像檔標籤	| `24.04` |
| 硬體設定	| `GPU.small` |
| 虛擬網路	| `bootcamp` +安全群組 |

確認後點擊左下角「**建立**」。

![檢閱並建立VM](images/nchc-19-vm-review.png)

### NCHC-11. 等待VM啟動並取得IP

建立後回到「虛擬機器管理」頁面，等待數分鐘，狀態由`build`變為**`active`**即表示VM已就緒。

點擊VM名稱進入詳細頁面，後續步驟將在此取得**浮動IP**。

![VM狀態active](images/nchc-20-vm-active.png)

進入VM詳細資料頁面，確認：

 -  **狀態**：`active`
 -  **登入帳號**：`ubuntu`

在「虛擬網路資訊」區塊中，點擊`bootcamp`列右側的「**&vellip；**」按鈕，選擇「**組態浮動IP**」。

![VM詳細資料&mdash;組態浮動IP](images/nchc-21-vm-detail.png)

在「組態浮動IP」對話框中選擇「**自動組態浮動IP**」，點擊「**確定**」。

![組態浮動IP](images/nchc-22-vm-floating-ip.png)

組態完成後，虛擬網路資訊欄位會顯示**浮動IP**（例如：`140.110.108.39`），此即為從外部SSH連線時使用的IP。

> [!IMPORTANT]
> **請記下或複製此浮動IP**，下一步SSH連線時會需要用到。

![浮動IP組態完成](images/nchc-23-vm-floating-ip-done.png)

### NCHC-12. SSH連線至VM

**先在本機開啟Terminal：**

| 平臺	        | 開啟方式 |
| ----	        | -------- |
| **Windows**	| 開始選單搜尋`PowerShell`或`cmd`，或安裝[Windows Terminal](https://aka.ms/terminal) |
| **macOS**	| `Spotlight` (`&#x2318; + Space`)搜尋`Terminal`，或至「應用程式&rarr;工具程式&rarr;終端機」 |
| **Linux**	| 快捷鍵`Ctrl + Alt + T`，或在應用程式選單中搜尋`Terminal` |

> Windows 10/11內建的PowerShell與cmd均支援`ssh`指令，無需額外安裝。

使用浮動IP從本機連線至VM：

```bash
ssh ubuntu@<浮動IP>
```

例如：

```bash
ssh ubuntu@140.110.108.39
```

輸入建立VM時設定的**密碼**即可登入。

> 密碼：`NCHCbootcamp2026_`

---


> [!NOTE]
> ...

> [!TIP]
> ...

> [!IMPORTANT]
> ...

> [!WARNING]
> ...

> [!CAUTION]
> ...
