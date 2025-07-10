try:
    from .dynamic_version import *
except ImportError:
    version = "develop"
    commit_hash = "develop"
