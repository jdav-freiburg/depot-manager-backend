try:
    from .dynamic_version import *
except ImportError:
    version: str = "develop"
    commit_hash: str = "develop"
