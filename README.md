# oauth.apisample.python

## Docker: Flask

```shell
docker build -t oauth.apisample.python-flask-dev .
```

## Docker: Nginx + Flask with Gunicorn

```shell
docker compose -f compose.yml -p "oauth-apisample-python" up -d
```