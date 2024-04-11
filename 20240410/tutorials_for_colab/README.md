
# Running CUDA-Q on [Colab](https://colab.research.google.com/)

Follow the steps below to run cudaq tutorials with free T4 GPU backend

<img src="https://github.com/Squirtle007/CUDA_Quantum/assets/66664309/d1cfbe1f-f354-45a7-8757-abb1a48a3395" width="800">

 1. Log in [Colab](https://colab.research.google.com/) and click on the **open notebook** under the **file** tab

    <img src="https://github.com/Squirtle007/CUDA_Quantum/assets/66664309/d96a3ae5-6110-4978-8d27-ff777d9c4014" width="800">

 2. To access tutorials in this repository, search this repository in the **GitHub** catalog with:

    ```
    Squirtle007/CUDA_Quantum
    ```
    <img src="https://github.com/Squirtle007/CUDA_Quantum/assets/66664309/103e2033-db95-4cbc-8f47-b0dc04748c8d" width="800">
    
 3. Make sure to select **Runtime** &rarr; **Change runtime type** &rarr; **T4 GPU** as the backend for acceleration

    <img src="https://github.com/Squirtle007/CUDA_Quantum/assets/66664309/18685649-25e9-4a7e-b117-340063b3650f" width="800">

    <img src="https://github.com/Squirtle007/CUDA_Quantum/assets/66664309/40e9d189-3a8d-4061-9f6e-5f9c98f12682" width="500">

 4. Set up CUDA Quantum properly in the Colab environment using the following commands (at the very beginning)

    ```
    !wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-keyring_1.0-1_all.deb
    !dpkg -i cuda-keyring_1.0-1_all.deb
    !apt-get update
    !apt-get -y install libcublas-11-8 libcusolver-11-8 cuda-cudart-11-8
    
    %pip install cuda-quantum==0.6.0
    ```
