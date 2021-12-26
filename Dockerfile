FROM python:3.9

WORKDIR app

RUN pip install pipenv

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv sync

# Set up a sample repo for cli testing
RUN mkdir cli-testing && \
     cd cli-testing && \
     git init && \
     git config --global user.email "flexlate-git@nickderobertis.com" && \
     git config --global user.name "flexlate-git" && \
     touch README.md && \
     git add -A && \
     git commit -m "Initial commit"

COPY . .
RUN pipenv run python upload.py --build-only
RUN pip install dist/flexlate*.whl
RUN fxt --install-completion bash

WORKDIR cli-testing