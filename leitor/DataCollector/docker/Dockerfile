#
# Dockerfile do sistema
#
# Autor: Alcindo Gandhi Barreto Almeida
# Data: 25/05/2023
#

FROM tiangolo/meinheld-gunicorn-flask:python3.9

COPY ./app/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app /app
