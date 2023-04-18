try:
    __version__ = __import__('pkg_resources') \
        .get_distribution('pelican').version
except Exception:
    __version__ = "unknown"
