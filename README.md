# DeepCreamPy-erogaki-wrapper

## Building the Docker Image

### 1. Model

**The Model isn't included with this repository, since we're unsure about its licensing.**

Get the following models and put them in the `models` directory:

- `09-11-2019 DCPv2 model`

You can find links to them [here](https://github.com/erogaki-dev/DeepCreamPy/blob/master/docs/INSTALLATION.md).

Your `models` directory should then have the following subdirectories:

- `09-11-2019 DCPv2 model/`

### 2. `docker image build`

Then just build the docker image, when you're in the root directory of this repository, using the following command:

```
docker image build -t deepcreampy-erogaki-wrapper .
```
