FROM python:3.9

# Install git 2.35.1 as that is what is in CI
RUN apt update
RUN apt install make libssl-dev libghc-zlib-dev libcurl4-gnutls-dev libexpat1-dev gettext unzip -y
RUN wget https://github.com/git/git/archive/v2.35.1.zip -O git.zip && \
    unzip git.zip && \
    cd git-* && \
    make prefix=/usr/local all && \
    make prefix=/usr/local install
RUN echo "Git version $(git --version)"

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