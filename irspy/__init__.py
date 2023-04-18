try:
    __version__ = __import__('pkg_resources').get_distribution('irspy').version
except Exception:
    __version__ = "unknown"
