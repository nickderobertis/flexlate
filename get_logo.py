import os
import pathlib

import requests

import conf

DOCS_OUT_FOLDER = pathlib.Path("docsrc") / "source" / "_static" / "images"
DOCS_OUT_PATH = DOCS_OUT_FOLDER / "logo.svg"


def download_logo(logo_url=conf.PACKAGE_LOGO_URL, out_path: str = str(DOCS_OUT_PATH)):
    if not logo_url:
        return

    print(f"Downloading logo from {logo_url}")
    response = requests.get(logo_url)
    if response.status_code != 200:
        raise NoLogoAtUrlException(logo_url)

    content = response.content.decode("utf8")
    with open(out_path, "w") as f:
        f.write(content)
    print(f"Logo outputted to {out_path}")


class NoLogoAtUrlException(Exception):
    pass


if __name__ == "__main__":
    if not os.path.exists(DOCS_OUT_FOLDER):
        os.makedirs(DOCS_OUT_FOLDER)

    download_logo()
