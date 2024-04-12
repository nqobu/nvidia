
# Running CUDA-Q on Taiwan Computing Cloud (TWCC)

Learn more about [CUDA-Q] and follow the steps below to set up:

 1. Sign up [TWCC](https://www.twcc.ai/)

    <img src="assets/step1.png" width="800">

 2. Log in and navigate to **Interactive Container** on the dashboard

    <img src="assets/step2.png" width="800">

 3. Select **CREATE** to set up a container

    <img src="assets/step3.png" width="800">

 4. Search and select **CUDA Quantum** then specify compute resources and storage, etc.

    <img src="assets/step4.png" width="800">

 5. Click on the container (after initialization) to see more details and **LAUNCH** Jupyter Notebook

    <img src="assets/step5.png" width="800">

 6. Within Jypyter Notebook open a **Terminal** and run the following commands to access built-in tutorials inside CUDA Quantum

    <img src="assets/step6.png" width="800">

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
