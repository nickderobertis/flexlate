from enum import Enum


class AddMode(str, Enum):
    LOCAL = "local"
    PROJECT = "project"
    USER = "user"