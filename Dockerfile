FROM python:3.10-alpine3.18

# upgrade pip
RUN pip install --upgrade pip && \
    pip install poetry==1.6.1

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# get curl for healthchecks
RUN apk add curl

# permissions and nonroot user for tightened security
RUN adduser -D nonroot
RUN mkdir /home/app/ && chown -R nonroot:nonroot /home/app
RUN mkdir -p /var/log/flask-app && touch /var/log/flask-app/flask-app.err.log && touch /var/log/flask-app/flask-app.out.log
RUN chown -R nonroot:nonroot /var/log/flask-app
WORKDIR /home/app
USER nonroot

# copy all the files to the container
COPY --chown=nonroot:nonroot pyproject.toml poetry.lock ./
RUN touch README.md

# venv
ENV VIRTUAL_ENV=/home/app/.venv \
    PATH="$VIRTUAL_ENV/bin:$PATH"

# python setup
RUN poetry install --without dev --no-root && \
    rm -rf $POETRY_CACHE_DIR

COPY --chown=nonroot:nonroot oauth_apisample_python ./oauth_apisample_python

RUN poetry install --without dev

CMD ["poetry", "run", "python", "-m", "oauth_apisample_python.app"]