FROM python:latest
ADD client/client.py /client/
WORKDIR /client/
EXPOSE 55555
ENTRYPOINT [ "python3", "-u", "client.py"]