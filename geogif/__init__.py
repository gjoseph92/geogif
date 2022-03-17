from .gif import dgif, gif

# Single-source version from pyproject.toml: https://github.com/python-poetry/poetry/issues/273#issuecomment-769269759
# Note that this will be incorrect for local installs
import importlib.metadata

__version__ = importlib.metadata.version("geogif")
del importlib


__all__ = ["gif", "dgif"]
