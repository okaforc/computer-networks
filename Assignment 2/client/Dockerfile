FROM python:latest
ADD client/client.py /client/
COPY res/ /client/
WORKDIR /client/
EXPOSE 54321
ENTRYPOINT [ "python3", "-u", "client.py"]