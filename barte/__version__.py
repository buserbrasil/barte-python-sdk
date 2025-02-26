from importlib.metadata import PackageNotFoundError, version


try:
    __version__ = version("barte-python-sdk")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"
