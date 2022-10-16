FROM python:latest
ADD client/client.py /client/
COPY res/ /client/
WORKDIR /client/
VOLUME ./rec_files:/rec_files
ENTRYPOINT [ "python3", "-u", "client.py"]