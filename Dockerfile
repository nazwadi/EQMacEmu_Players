# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-slim

EXPOSE 8000

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /app

ARG USERNAME=appuser
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && chown $USERNAME:$USERNAME /app

# Install dependencies
COPY requirements.txt /app/
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc pkg-config libmariadb-dev libmariadb3 \
    && python -m pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y gcc pkg-config libmariadb-dev \
    && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Copy the project code into the container
COPY --chown=$USERNAME:$USERNAME . /app

USER $USERNAME

RUN mkdir -p /app/uploads

RUN python manage.py collectstatic --noinput

CMD ["sh", "scripts/start.sh"]
