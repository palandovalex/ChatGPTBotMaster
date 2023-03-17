FROM python:3.10.10-slim-buster
WORKDIR /app
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH "/root/.local/bin:$PATH"
COPY ./.env ./whiteList.txt ./poetry.lock ./pyproject.toml ./

RUN poetry env use 3.10 && poetry install

VOLUME ./.sessions /app/.sessions
VOLUME ./chatgptbot /app/chatgptbot

ENTRYPOINT poetry run python3 chatgptbot/chatbot.py

