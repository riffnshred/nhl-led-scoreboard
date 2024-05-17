# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.9-slim

RUN apt-get update && apt-get install -y dbus libdbus-glib-1-dev libgirepository1.0-dev libdbus-1-dev python3-dev python3-cairosvg

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app
RUN cd /app/submodules/matrix/ && make build-python
RUN cd /app/submodules/matrix/ && pip install bindings/python/

# Creates a non-root user with an explicit UID and adds permission to access the /app folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN adduser -u 5678 --disabled-password --gecos "" appuser && chown -R appuser /app
# USER root

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "src/main.py", "--terminal-mode=true"]
