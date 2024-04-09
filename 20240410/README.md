# NCHC Quantum Computing Bootcamp 2024

量子技術快速發展，高效能運算模擬推進了量子研究的突破。為了滿足量子應用、演算法甚至量子硬體的開發，新型量子運算平臺至關重要。[CUDA Quantum] 提供開發人員所需的統一軟體平臺，能將古典計算與量子計算整合為一，對於推動量子系統的開發更加便利。

在這次活動的上半場，將會先簡介 NVIDIA Quantum Platform，可藉著個機會了解 NVIDIA 在量子研究中各種有用的軟硬體工具，緊接著深入熟悉 [CUDA Quantum] 的運作原理與功能。

而在這次活動的下半場，將透過實作課程，讓大家練習如何運用 [CUDA Quantum] 來進行各式量子計算與應用，包含混和量子-古典神經網路，以及多 GPU 加速的量子模擬，實現分散式量子運算，引領您從三維世界一窺高維 Hilbert Space 裡的好玩工具 -- [CUDA Quantum](https://github.com/NVIDIA/cuda-quantum "C++ and Python support for the CUDA Quantum programming model for heterogeneous quantum-classical workflows")。

[CUDA Quantum]: https://developer.nvidia.com/cuda-q

 -  活動日期: 2024/04/10（三）10:00--16:00
 -  活動地點: 國網中心新竹本部—新竹市東區研發六路7號，B 教室
 -  人數限制: 40 人次
 -  課程規劃: 

| 時間                | 活動內容                                               |
| ------------------- | ------------------------------------------------------ |
| 10:30 AM - 10:45 AM | 歡迎                                                   |
| 10:45 AM - 11:00 AM | NVIDIA Quantum Platform Overview                       |
| 11:00 AM - 12:00 PM | CUDA Quantum & cuQuantum                               |
| 12:00 PM - 13:30 PM | 用餐                                                   |
| 13:30 PM - 14:00 PM | 軟體環境說明和建置                                     |
| 14:00 PM - 14:30 PM | 實作:CUDA Quantum 基礎                                 |
| 14:30 PM - 14:50 PM | 實作：Hybrid Quantum Neural Networks with CUDA Quantum |
| 14:50 PM - 15:10 PM | 進階實作：Multi-GPU Acceleration by CUDA Quantum       |
| 15:10 PM - 15:30 PM | Q&A + 交流時間                                         |

---

# Running CUDA-Q on Taiwan Computing Clond (TWCC)

Learn more about [CUDA-Q](https://developer.nvidia.com/cuda-q) and follow the steps below to set up:

 1. Sign up [TWCC](https://www.twcc.ai/)

    <img src="https://github.com/Squirtle007/CUDA_Quantum/assets/66664309/225641a3-c7ad-4547-86c3-f1ecdbf308f3" width="800">

 2. Log in and navigate to **Interactive Container** on the dashboard

    <img src="https://github.com/Squirtle007/CUDA_Quantum/assets/66664309/03a3c1ed-1387-4ba1-be50-65e0983e76c7" width="800">

 3. Select **CREATE** to set up a container

    <img src="https://github.com/Squirtle007/CUDA_Quantum/assets/66664309/6a647a07-7a48-41a7-97b8-efee2c0a5dc2" width="800">

 4. Search and select **CUDA Quantum** then specify compute resources and storage, etc.

    <img src="https://github.com/Squirtle007/CUDA_Quantum/assets/66664309/935cc1b2-19d4-4e3e-8cb4-e41d2a40a7d9" width="800">

 5. Click on the container (after initialization) to see more details and **LAUNCH** Jupyter Notebook

    <img src="https://github.com/Squirtle007/CUDA_Quantum/assets/66664309/14aed847-6301-4e7e-bb13-5e309cf107f4" width="800">

 6. Within Jypyter Notebook open a **Terminal** and run the following commands to access built-in tutorials inside CUDA Quantum

    <img src="https://github.com/Squirtle007/CUDA_Quantum/assets/66664309/b7fe4abb-8c91-4655-941f-e55a5230c7d7" width="600">

    ```shell
    sudo chown -R `stat . -c %u:%g` /home/cudaq/
    cp -r /home/cudaq/ ~/cudaq
    ```

 7. To access additional tutorials in this repository, use the following `git clone` command

    ```shell
    git clone https://github.com/Squirtle007/CUDA_Quantum.git
    ```

<!--
  vim: ft=markdown ic wrap noet norl sw=8 ts=8 sts=4:
  -->
