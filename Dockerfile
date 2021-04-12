FROM continuumio/miniconda3

## Setup first part of DeepCreamPy-erogaki-wrapper.
WORKDIR /app

# Create the conda environment.
RUN conda create --name DeepCreamPy-erogaki-wrapper python=3.6.7

## Setup DeepCreamPy.
WORKDIR /app/DeepCreamPy

# Copy the requirements file.
COPY ./DeepCreamPy/requirements-cpu.txt ./

# Install the dependencies.
RUN conda run --name DeepCreamPy-erogaki-wrapper pip install -r requirements-cpu.txt

# Copy the source code.
COPY ./DeepCreamPy ./

## Setup second part DeepCreamPy-erogaki-wrapper.
WORKDIR /app

# Copy the source code.
COPY ./src ./

# Start DeepCreamPy-erogaki-wrapper.
ENTRYPOINT ["conda", "run", "--name", "DeepCreamPy-erogaki-wrapper", "python", "wrapper_main.py"]
