FROM python:latest
ADD control/control.py /control/
WORKDIR /control/
EXPOSE 54321
ENTRYPOINT [ "python3", "-u", "control.py"]