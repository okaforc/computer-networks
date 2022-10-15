FROM python:latest
ADD client/client.py /client/
COPY res/ /client/
WORKDIR /client/
ENTRYPOINT [ "python3", "-u", "client.py"]