import os


def is_running_on_ci() -> bool:
    ci = os.environ.get("CI")
    return ci == "true"


if __name__ == '__main__':
    print(is_running_on_ci())