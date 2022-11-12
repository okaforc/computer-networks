FROM python:latest
ADD fwd/fwd.py /fwd/
WORKDIR /fwd/
EXPOSE 54321/udp
ENTRYPOINT [ "python3", "-u", "fwd.py"]