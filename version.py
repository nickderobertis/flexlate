from pathlib import Path

setup_cfg_path = Path(__file__).parent / "setup.cfg"


def get_version() -> str:
    if not setup_cfg_path.exists():
        return "0.0.1"
    with open(setup_cfg_path) as f:
        for line in f:
            if line.startswith("version"):
                return line.split("=")[1].strip()
    raise ValueError("could not find version in setup.cfg")


if __name__ == "__main__":
    print(get_version())
