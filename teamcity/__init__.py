# coding=utf-8
__all__ = ['is_running_under_teamcity']

import os

TEAMCITY_ENV_PROJECT_NAME = "TEAMCITY_PROJECT_NAME"


def is_running_under_teamcity():
    return os.getenv(TEAMCITY_ENV_PROJECT_NAME) is not None
