# Download bootcamp contents

```shell
git clone https://github.com/openhackathons-org/End-to-End-AI-for-Science
sudo ln -s $PWD/End-to-End-AI-for-Science/workspace /.
```

# Libraries Installation

```shell
pip3 install gdown ipympl cdsapi
pip3 install wandb ruamel.yaml netCDF4 mpi4py cdsapi
pip3 install --upgrade nbconvert
```

# Dataset Installation

```shell
python3 /workspace/python/source_code/dataset.py
```

# Uncompresses the Dataset 

```shell
python3 /workspace/python/source_code/fourcastnet/decompress.py
```

# Purge Files

```shell
rm -rf /workspace/python/source_code/fourcastnet/pre_data
```
