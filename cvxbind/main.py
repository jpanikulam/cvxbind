import os
import argparse
from utils import Log
from parse_cvxgen import ParseCVX
from gen_cpp import GenCPP


def main():
    parser = argparse.ArgumentParser(description='CVXGEN Python Binding Generator')
    parser.add_argument('path', metavar='path', default='./images',
                        help='Give the target path')
    parser.add_argument('-v', '--verbose', action='store_true', default=False,
                        help='Decide verbosity')
    args = parser.parse_args()
    Log.set_verbose(args.verbose)
    path = os.path.realpath(args.path)
    parsed_cvx = ParseCVX.read_file(path)
    write_text = GenCPP.make_cvx_binding(parsed_cvx)
    print write_text


if __name__ == '__main__':
    main()
