# NCHC VCS - NVIDIA NIMS SETUP GUIDE

Will setup 2 NIMs + 1 BioNeMo Container for protein design:
- [rfdiffusion](https://build.nvidia.com/ipd/rfdiffusion)
- [proteinmpnn](https://build.nvidia.com/ipd/proteinmpnn)
- [bionemo framework](https://github.com/NVIDIA/bionemo-framework)

see more NIMs in [documentation](https://docs.nvidia.com/nim/index.html#bionemo); 

more BioNeMo in [documentation](https://docs.nvidia.com/bionemo-framework/latest/).

## Prerequisites - TWCC VCS Setup

### Create VCS Instance (Image Type: Ubuntu)

- `BASICS`
    - Image info = 
(public)Ubuntu-24.04-20240913
    - Basic Configuration = vgv.xsuper
- `VIRTUAL NETWORK INTERFACE`
    - Assign Public IP = Auto-asign Floating IP
- `KEY PAIR`
    - follow [doc](https://man.twcc.ai/@twccdocs/doc-vcs-main-zh/https%3A%2F%2Fman.twcc.ai%2F%40twccdocs%2Fguide-vcs-keypair-zh) to create one.
- `INITIAL SCRIPTS`
    - follow [doc](https://man.twcc.ai/@twccdocs/doc-vcs-main-zh/https%3A%2F%2Fman.twcc.ai%2F%40twccdocs%2Fhowto-vcs-gpu-driver-via-initial-scripts-zh) to install a NVIDIA GPU Driver.
- click on `CREATE`

see more VCS tutorials made by TWCC on [YouTube](https://www.youtube.com/watch?v=BNQ7npYQDSo&list=PLYcc4OEy5lEDzfHqN79Yu1KHXbRFVRtdX&index=1&ab_channel=%E5%9C%8B%E7%B6%B2%E4%B8%AD%E5%BF%83-iService).

### Remote Access VM and Setup Docker 

After your VM's state show `Active`, In `BASICS` tab, click `CONNECT` to have your VM public IP. Launch your local terminal, and ssh to the remote VM.

```bash
ssh -i <your ssh private key> ubuntu@<YOUR VM PUBLIC IP>
```

if GPU driver not ready, follow [Installation Guide](https://man.twcc.ai/@twccdocs/doc-vcs-main-zh/https%3A%2F%2Fman.twcc.ai%2F%40twccdocs%2Fhowto-vcs-install-nvidia-gpu-driver-zh) to install NVIDIA GPU Driver. see example below:

```bash
echo "blacklist nouveau" | sudo tee /etc/modprobe.d/blacklist-nouveau.conf && echo "options nouveau modeset=0" | sudo tee -a /etc/modprobe.d/blacklist-nouveau.conf && sudo update-initramfs -u && sudo modprobe -r nouveau && sudo modprobe nouveau && sudo apt-get update && sudo apt-get install libc-dev -y && sudo apt-get install linux-headers-$(uname -r) -y && wget https://tw.download.nvidia.com/tesla/550.90.07/NVIDIA-Linux-x86_64-550.90.07.run && sudo sh NVIDIA-Linux-x86_64-550.90.07.run --accept-license --no-questions --dkms -s
```

follow [Installation Guide](https://docs.nvidia.com/ai-enterprise/deployment/vmware/latest/docker.html) to install Docker and NVIDIA Container Toolkit. see example below:

```bash
# install docker
curl -fsSL get.docker.com | bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
## verfiy docker is ready
docker run hello-world
# install NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
  && curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
## verify docker with nvidia container toolkit
docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi
```

## Setup NVIDIA NIM and BioNeMo Container

### SSH to your VM

if you are using a prebuilt VM image `(private)nims20241129v1`, please download ans use the ssh key as below:

```bash
wget https://gist.githubusercontent.com/chychen/882f7b4cf4a3ff647667d2f54740e2af/raw/38b6cfdac50a20d29894190e94287b5a05bf7278/id_rsa
chmod 600 id_rsa
ssh -i id_rsa ubuntu@<YOUR VM PUBLIC IP> 
```

otherwise:

```bash
ssh -i <your ssh private key> ubuntu@<YOUR VM PUBLIC IP>
```

### Firstly, have Free Developer API Key Ready

- Access to NVIDIA NIM Now Available Free to Developer Program Members
[https://developer.nvidia.com/blog/access-to-nvidia-nim-now-available-free-to-developer-program-members/?ncid=ref-dev-240225](https://developer.nvidia.com/blog/access-to-nvidia-nim-now-available-free-to-developer-program-members/?ncid=ref-dev-240225)
- A Recording to demo [how to setup NVIDIA NIMs on TWCC VCS](https://www.youtube.com/watch?v=geZfrPC_lic&ab_channel=JayChen%40NVIDIA) with a prebuilt VM Image.

### Setup Keys

- [rfdiffusion doc](https://docs.nvidia.com/nim/bionemo/rfdiffusion/latest/quickstart-guide.html)
- [proteinmpnn doc](https://docs.nvidia.com/nim/bionemo/proteinmpnn/latest/quickstart-guide.html)

log in with your NGC API (enter the key as password when prompted.)

```bash
docker login nvcr.io --username='$oauthtoken'
## Password: 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
## Only valid for this workshop.
```

It is recommended to add the following environment variables to your `~/.bashrc` file, enabling them to auto-load in every bash session.

```bash
vim ~/.bashrc
```

Make sure following KEYs are set within your `~/.bashrc` file.

```bash
## Env Variables
export NGC_API_KEY=<your personal NIM Self-Hosted API key>
export NGC_CLI_API_KEY=<your personal NIM Self-Hosted API key>
export NVCF_RUN_KEY=<your personal NIM Hosted API key>
export LOCAL_NIM_CACHE=~/.cache/nim
```

update env vars:

```bash
source ~/.bashrc
```

Skip this one if you already have the folder `$LOCAL_NIM_CACHE` ready:

```bash
if [ -d "$LOCAL_NIM_CACHE" ]; then
    echo "Folder exists: $LOCAL_NIM_CACHE"
else
    echo "Folder does not exist. Creating folder: $LOCAL_NIM_CACHE"
    mkdir -p "$LOCAL_NIM_CACHE"
    sudo chmod -R 0777 "$LOCAL_NIM_CACHE"
fi
```

### Optionally, download pre-built engines to speedup the setup.

When you launch NIM for the first time, it will generate TensorRT engines tailored to your GPU, significantly optimizing inference performance (often exceeding a 2X improvement). To save time during the workshop, we have pre-built these engines for you. (Please note that the pre-built files are only valid for the duration of the workshop. You can skip this step now and easily build your own engines in the next step.)

```bash
sudo apt install python3.12-venv
python3 -m venv ~/dev
~/dev/bin/pip3 install gdown
~/dev/bin/gdown 1_DnjziB4DpxxKZs3UUzZqvY9XAA1-ehv
sudo apt install unzip
unzip cache_nim.zip
mv .cache/nim/ ~/.cache/.
```

### Build your own VM image

At this stage, it is recommended to create a VM image to avoid repeating the above steps in the future. Please refer to the [documentation](https://man.twcc.ai/@twccdocs/doc-vcs-main-zh/https%3A%2F%2Fman.twcc.ai%2F%40twccdocs%2Fhowto-vcs-resize-instance-zh) for guidance on creating your own VM image.

### In VM, Launch 2 NIMs + 1 BioNeMo FW Container and Jupyter Lab

- `port 8002` for `rfdiffusion` NIM
- `port 8003` for `proteinmpnn` NIM
- `cloud hosted api` for `esmfold` NIM

```bash
## launch rfdiffusion on port 8002
docker run -d \
    --runtime=nvidia \
    --gpus='"device=0"' \
    -p 8002:8000 \
    -e NGC_API_KEY \
    -v "$LOCAL_NIM_CACHE":/opt/nim/.cache \
    nvcr.io/nim/ipd/rfdiffusion:2
## launch proteinmpnn on port 8003
docker run -d \
    --runtime=nvidia \
    --gpus='"device=0"' \
    -p 8003:8000 \
    -e NGC_CLI_API_KEY \
    -v "$LOCAL_NIM_CACHE":/home/nvs/.cache/nim \
    nvcr.io/nim/ipd/proteinmpnn:1.0.0
## launch bionemo conatiner and jupyter lab
docker run -d --gpus all --network host  -e NGC_CLI_API_KEY -v $PWD:$PWD   nvcr.io/nvidia/clara/bionemo-framework:2.1 jupyter lab --allow-root --ip=0.0.0.0 --port=8888 --no-browser --NotebookApp.token='' --NotebookApp.allow_origin='*' --ContentsManager.allow_hidden=True --notebook-dir=$PWD
```

Use `docker ps` to view running containers. You should see output similar to the following:

```bash
docker ps
```

An example:
```
#CONTAINER ID   IMAGE                                        COMMAND                   CREATED          STATUS          PORTS                                         NAMES
#baa6ae96777e   nvcr.io/nvidia/clara/bionemo-framework:2.1   "/opt/nvidia/nvidia_…"    6 seconds ago    Up 2 seconds                                                  hopeful_murdock
#ba1723a2d962   nvcr.io/nim/ipd/proteinmpnn:1.0.0            "/opt/nvidia/nvidia_…"    10 seconds ago   Up 8 seconds    0.0.0.0:8001->8000/tcp, [::]:8001->8000/tcp   brave_ptolemy
#b4ad6b6858e6   nvcr.io/nim/ipd/rfdiffusion:2                "/bin/sh -c 'exec \"$…"   18 seconds ago   Up 16 seconds   0.0.0.0:8000->8000/tcp, :::8000->8000/tcp     practical_elbakyan
```

Wait about one minute for launching NIMs service, and then use `curl` to check API health status:

```bash
# check rfdiffusion
curl http://localhost:8002/v1/health/ready
# check proteinmpnn
curl http://localhost:8003/v1/health/ready
```

An example:

```
#{"status":"ready"}
#{"status":"ready"}
```

### Develop on your own client device.

setup ssh tunneling, port forwarding jupyter lab to localhost. use below command on client terminal. 
``` 
ssh -i <your ssh private key> -fNL 8888:localhost:8888 ubuntu@<YOUR VM PUBLIC IP>
```

open your browser: http://localhost:8888

### How to stop containers?
 
Use `docker stop <CONTAINER ID>` to stop one or `docker stop $(docker ps -aq)` to stop all.

```bash
docker stop $(docker ps -aq)
```