# Download Files and Dataset

```shell
git clone https://github.com/openhackathons-org/End-to-End-AI-for-Science
sudo ln -s $PWD/End-to-End-AI-for-Science/workspace /.
```

# Install Libraries

```shell
pip3 install gdown ipympl cdsapi
pip3 install wandb ruamel.yaml netCDF4 mpi4py cdsapi
pip3 install --upgrade nbconvert
```

# Install Dataset

```shell
python3 /workspace/python/source_code/dataset.py
```

# Decompress the Dataset 

```shell
python3 /workspace/python/source_code/fourcastnet/decompress.py
```

# Purge Data Files

```shell
rm -rf /workspace/python/source_code/fourcastnet/pre_data
```

<!--
  vim:  ft=markdown ic noet norl wrap sw-8 ts=8 sts=4:
  --->
