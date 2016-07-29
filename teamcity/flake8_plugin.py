try:
    from flake8.formatting import base  # noqa
except ImportError:
    from .flake8_v2_plugin import *  # noqa
else:
    from .flake8_v3_plugin import *  # noqa
