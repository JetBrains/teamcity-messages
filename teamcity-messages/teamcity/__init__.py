__all__ = ['underTeamcity']

import os

TEAMCITY_ENV_PROJECT_NAME = "TEAMCITY_PROJECT_NAME"

def underTeamcity():
    return os.getenv(TEAMCITY_ENV_PROJECT_NAME) is not None
