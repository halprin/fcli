FROM python:3-alpine

RUN pip install fcli

VOLUME ["/root/.fcli"]

ENTRYPOINT ["fcli"]
