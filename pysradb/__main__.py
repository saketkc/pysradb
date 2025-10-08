import sys

from .cli import parse_args

if __name__ == "__main__":
    parse_args(sys.argv[1:])
