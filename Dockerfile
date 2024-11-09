FROM python:3.12-alpine as venv

LABEL maintainer="Jan Willhaus <mail@janwillhaus.de>"

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV POETRY_VERSION=1.8.2

WORKDIR /src
COPY pyproject.toml poetry.lock ./

RUN set -e; \
    apk add build-base libffi-dev; \
    pip install -U --no-cache-dir pip "poetry~=$POETRY_VERSION"; \
    python -m venv /venv; \
    . /venv/bin/activate; \
    poetry install \
        --no-interaction \
        --no-directory \
        --no-root \
        --only main

FROM python:3.12-alpine

ENV PATH=/venv/bin:$PATH

COPY --from=venv /venv /venv
COPY ./src /app


ENTRYPOINT [ "uvicorn", "src.main:app"]
CMD [ "--host", "0.0.0.0" ]
