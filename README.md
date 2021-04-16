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

## Running a Docker Container

Once you build the Docker image, you can just run a container like this:

```
docker run -it --network=host deepcreampy-erogaki-wrapper
```

## Using the `Dockerfile-dev`

The `Dockerfile-dev` is intended to make it easy to develop erogaki dev libraries like `erogaki-wrapper-shared-python`.

To build an image using this Dockerfile, make sure everything is setup as in "Building the Docker Image -> 1. Model".

Then place your packaged development version of `erogaki-wrapper-shared-python` in `./dev` and name it as follows: `erogaki_wrapper_shared_python-9999-py3-none-any.whl`

After you've done that, just build the docker image like so:

```
docker image build -f Dockerfile-dev -t deepcreampy-erogaki-wrapper:dev .
```

And run a container like this:

```
docker run -it --network=host deepcreampy-erogaki-wrapper
```
