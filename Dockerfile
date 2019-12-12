# Base image to python 3.6-slim
FROM python:3.6-slim

# Maintainer
MAINTAINER Adrian Diaz

VOLUME ["/src/output"]

# Copy requirements source code to SRCDIR
COPY ./requirements.txt /src/requirements.txt

# Install Requirements.
RUN pip install -r /src/requirements.txt

COPY . /src
WORKDIR /src

CMD ["python" ,"main.py"]