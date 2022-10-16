FROM python:latest
ADD worker/worker.py /worker/
COPY res/ /worker/
ADD worker/files/ /worker/files/
WORKDIR /worker/
ENTRYPOINT [ "python3", "-u", "worker.py"]