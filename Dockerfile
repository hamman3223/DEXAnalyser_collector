FROM harbor.rvision.pro/sec/python-librdkafka:1.9.2

ARG UUID=1000
ARG GID=1000

ARG APPUSER=python
ARG GROUP=python
ENV PYTHONUNBUFFERED 1
ENV PATH="$PATH:/home/${APPUSER}/.local/bin"

WORKDIR /application

# Копируем весь проект с правами пользователя
COPY --chown=$APPUSER:$GROUP . /application/

# Скачиваем poetry, устанавливаем зависимости
RUN pip install poetry==1.2.2  && \
    poetry config virtualenvs.in-project true &&\
    poetry install --only main

ENTRYPOINT poetry run python src/main.py
