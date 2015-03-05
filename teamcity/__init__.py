# coding=utf-8
import os

__all__ = ['is_running_under_teamcity']

teamcity_presence_env_var = "TEAMCITY_VERSION"


def is_running_under_teamcity():
    return os.getenv(teamcity_presence_env_var) is not None
