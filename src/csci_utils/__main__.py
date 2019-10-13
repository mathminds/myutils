"""
Entrypoint module, in case you use `python -mcsci_utils`.


Why does this file exist, and why __main__? For more info, read:

- https://www.python.org/dev/peps/pep-0338/
- https://docs.python.org/2/using/cmdline.html#cmdoption-m
- https://docs.python.org/3/using/cmdline.html#cmdoption-m
"""
from csci_utils.cli import main

if __name__ == "__main__":
    # from pkg_resources import get_distribution, DistributionNotFound
    #
    # try:
    #     __version__ = get_distribution(__name__).version
    #
    # except DistributionNotFound:
    #     print("package is not installed")
    #     pass

    main()

