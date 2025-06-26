FROM python:3.13-slim

RUN apt update && apt install -y curl

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python - && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy using poetry.lock* in case it doesn't exist yet
COPY ./pyproject.toml ./poetry.lock /app/

WORKDIR /app

RUN poetry install --no-root

COPY ./depot_server /app/depot_server

ENV MODULE_NAME=depot_server.api
ENV VARIABLE_NAME=app

CMD ["uvicorn", "depot_server.api:app", "--host", "0.0.0.0", "--port", "80", "--log-level", "debug"]