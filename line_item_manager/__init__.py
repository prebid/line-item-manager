"""Top-level package for line-item-manager."""

__author__ = """the prebid contributors"""
__email__ = 'info@prebid.org'
__version__ = '0.2.10'

# For an official release, use dev_version = ''
dev_version = '3'

version = __version__
if dev_version:
    version = f'{__version__}-dev{dev_version}'
