FROM python:3.12.3-slim-bullseye as base

ARG DEV=false
ARG SERVICE_NAME
ENV VIRTUAL_ENV=/poetry_venv 
ENV PATH="${VIRTUAL_ENV}/bin:$PATH"
ENV APP_HOME=/${SERVICE_NAME}/app

FROM base as dev

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        build-essential

ENV POETRY_VERSION=1.8.3
RUN pip install poetry==$POETRY_VERSION

ENV PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=0 \
    POETRY_VIRTUALENVS_CREATE=0 \
    POETRY_CACHE_DIR=/tmp/poetry_cache
    
COPY /data_models /data_models/
COPY /crypto_lib /crypto_lib/

WORKDIR $APP_HOME

COPY ${APP_HOME}/pyproject.toml ${APP_HOME}/poetry.lock ./

RUN python3 -m venv $VIRTUAL_ENV \
    && . $VIRTUAL_ENV/bin/activate 

RUN if [ "$DEV" = "true" ]; then \
        poetry lock --no-update && poetry install --with dev --no-root && rm -rf $POETRY_CACHE_DIR; \
    else \
        poetry lock --no-update && poetry install --without dev --no-root && rm -rf $POETRY_CACHE_DIR; \
    fi

COPY ${APP_HOME}/ ./

RUN if [ "$DEV" = "true" ]; then \
    poetry lock --no-update && poetry install --with dev; \
    fi
  
#ENTRYPOINT ["poetry", "run", "start_dev"]
ENTRYPOINT [ "tail", "-F", "anything"]
  
FROM base as production

COPY --from=dev ${VIRTUAL_ENV} ${VIRTUAL_ENV}
WORKDIR /app
COPY ${APP_HOME}/src ./
EXPOSE 8080
ENTRYPOINT [ "hypercorn", "--bind", "0.0.0.0:8080", "asgi:production_app"]
#ENTRYPOINT [ "tail", "-F", "anything"]