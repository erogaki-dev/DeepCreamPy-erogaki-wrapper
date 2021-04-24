# DeepCreamPy-erogaki-wrapper

## Using the Dockerfile

### 1. Building the Docker Image

Just build the docker image, when you're in the root directory of this repository, using the following command:

```
docker image build -t deepcreampy-erogaki-wrapper .
```

### 2. Getting the Model Ready

**The Model isn't included with this repository, since we're unsure about its licensing.**

Create a Docker volume for the models (this volume can be shared with other parts of the erogaki infrastructure):

```
docker volume create erogaki-models
```

Get the following model and put it in the `erogaki-models` docker volume (find out the mountpoint using `docker volume inspect erogaki-models`):

- `09-11-2019 DCPv2 model`

You can find links to them [here](https://github.com/erogaki-dev/DeepCreamPy/blob/master/docs/INSTALLATION.md).

Your `erogaki-models` volume should then have the following subdirectories:

- `09-11-2019 DCPv2 model/`

### 3. Running the container

Then finally run the container like so:

```
docker run -it -v erogaki-models:/model --network=host deepcreampy-erogaki-wrapper
```

## Using the `Dockerfile-dev`

The `Dockerfile-dev` is intended to make it easy to develop erogaki dev libraries like `erogaki-wrapper-shared-python`.

To build an image using this Dockerfile, make sure you've done everything in "Using the Dockerfile -> 2. Getting the Model Ready".

Then place your packaged development version of `erogaki-wrapper-shared-python` in `./dev` and name it as follows: `erogaki_wrapper_shared_python-9999-py3-none-any.whl`

After you've done that, just build the docker image like so:

```
docker image build -f Dockerfile-dev -t deepcreampy-erogaki-wrapper:dev .
```

And run a container like this:

```
docker run -it -v erogaki-models:/model --network=host deepcreampy-erogaki-wrapper
```
