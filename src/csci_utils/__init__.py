# __version__ = '0.0.0'
from setuptools_scm import get_version
__version__ = get_version()
#
# from pkg_resources import get_distribution, DistributionNotFound
# try:
#     __version__ = get_distribution(__name__).version
# except DistributionNotFound:
#     # package is not installed
#     pass
