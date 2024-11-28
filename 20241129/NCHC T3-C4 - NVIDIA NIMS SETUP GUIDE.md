# NVIDIA NIMS SINGULARITY SETUP GUIDE for 台灣衫三號生醫專用節點

Will setup 2 NIMs for protein design:
- [rfdiffusion](https://build.nvidia.com/ipd/rfdiffusion)
- [proteinmpnn](https://build.nvidia.com/ipd/proteinmpnn)

see more NIMs [documentation](https://docs.nvidia.com/nim/index.html#bionemo)

## Prerequisites

- A Ubuntu environment with [docker](https://docs.docker.com/engine/install/ubuntu/) and [singularity](https://docs.sylabs.io/guides/latest/user-guide/) ready.

## Download NIMs' docker images 

### Have Free Developer API Key Ready

- Access to NVIDIA NIM Now Available Free to Developer Program Members
[https://developer.nvidia.com/blog/access-to-nvidia-nim-now-available-free-to-developer-program-members/?ncid=ref-dev-240225](https://developer.nvidia.com/blog/access-to-nvidia-nim-now-available-free-to-developer-program-members/?ncid=ref-dev-240225)

### Download NIMs' docker images from 

Pull and run / using Docker

```bash
docker login nvcr.io --username='$oauthtoken'
#Password: <PASTE_API_KEY_HERE>
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

### Download NIMs' docker images

```bash
docker pull nvcr.io/nim/ipd/rfdiffusion:2
docker pull nvcr.io/nim/ipd/proteinmpnn:1.0.0
```

## Convert docker images to Singularity Image Format (SIF) files

```bash
singularity -d build nim-ipd-rfdiffusion-2.sif docker-daemon://nvcr.io/nim/ipd/rfdiffusion:2
singularity -d build nim-ipd-proteinmpnn-1.sif docker-daemon://nvcr.io/nim/ipd/proteinmpnn:1.0.0
```

## Copy to Taiwania3 T3-C4 cluster

```bash
scp -r nim-ipd-rfdiffusion-2.sif <your account>@t3-c4.nchc.org.tw:~/
scp -r nim-ipd-proteinmpnn-1.sif <your account>@t3-c4.nchc.org.tw:~/
```

## Launch NIMs on Taiwania3 T3-C4 cluster

### Access to Cluster and Setup Keys

```bash
ssh <your account>@t3-c4.nchc.org.tw
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

Skip this one if you already have the folder `$LOCAL_NIM_CACHE/ws` ready:

```bash
if [ -d "$LOCAL_NIM_CACHE/ws" ]; then
    echo "Folder exists: $LOCAL_NIM_CACHE/ws"
else
    echo "Folder does not exist. Creating folder: $LOCAL_NIM_CACHE/ws"
    mkdir -p $LOCAL_NIM_CACHE/ws
    sudo chmod -R 0777 "$LOCAL_NIM_CACHE"
fi
```

### Launch NIMs by Singularity

at this point, we could only launch NIMs on login nodes due to the limitation of networking in compute nodes, please contact NCHC for more details.

- `port 8002` for `rfdiffusion` NIM
- `port 8003` for `proteinmpnn` NIM

```
## launch rfdiffusion on port 8002
singularity exec --nv -B $LOCAL_NIM_CACHE/ws:/opt/nim/workspace -B "$LOCAL_NIM_CACHE":/opt/nim/.cache nim-ipd-rfdiffusion-2.sif bash -c 'export NIM_HTTP_API_PORT=8002 NGC_API_KEY=$NGC_API_KEY && cd /opt/nim/ && start_server'
## launch proteinmpnn on port 8003
singularity exec --nv -B $LOCAL_NIM_CACHE:/home/nvs/.cache/nim nim-ipd-proteinmpnn-1.sif bash -c "export NIM_HTTP_API_PORT=8003 NGC_API_KEY=$NGC_API_KEY && start_server"
```

Wait about one minute for launching NIMs service, and then use `curl` to check API health status:

```bash
# check rfdiffusion
curl http://localhost:8002/v1/health/ready
# check proteinmpnn
curl http://localhost:8003/v1/health/ready
```