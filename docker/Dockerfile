FROM ubuntu:20.04

ENV PYTHONPATH=/workspace/app:${PATH}

RUN apt-get -qq update && apt-get install -y python3-pip

WORKDIR /workspace

COPY ./requirements/requirements.txt /workspace/requirements/requirements.txt
COPY ./app /workspace/app
COPY ./config /workspace/config

RUN pip3 install -r ./requirements/requirements.txt

WORKDIR /workspace/app

ENTRYPOINT ["python3", "main.py"]
