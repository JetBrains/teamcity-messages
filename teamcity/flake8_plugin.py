try:
    from flake8.formatting import base
except ImportError:
    from flake8_v2_plugin import *
else:
    from flake8_v3_plugin import *
