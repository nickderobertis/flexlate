# TODO: get version statically inside package by restructuring template
import pkg_resources


def get_flexlate_version() -> str:
    return pkg_resources.get_distribution("flexlate").version
