FROM python:latest
ADD worker/worker.py /worker/
COPY res/ /worker/
ADD worker/files/ /worker/
WORKDIR /worker/
ENTRYPOINT [ "python3", "-u", "worker.py"]