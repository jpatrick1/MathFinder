#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Code to clean data prior to calling MathFinder

Attributes
----------
LOG : logging.Logger
    Module logger
"""
import os
import shutil
import argparse
import logging
import py_meds.util as util

LOG = logging.getLogger(__name__)


def parse_args():
    """
    Parse input arguments
    Returns
    -------
    args : object
        Parsed args
    """
    h = {
        "program": "PyFinder",
        "input-path": "Root path of input images",
        "output-path": "Output path for training data",
        "force": "Removes output path without prompting if it exists", }

    parser = argparse.ArgumentParser(description=h['program'], formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--input-path', dest='input_path', help=h['input-path'], type=str, required=True)
    parser.add_argument('--output-path', dest='output_path', help=h['output-path'], type=str, required=True)
    parser.add_argument('--force', help=h['force'], action='store_true')

    args = parser.parse_args()

    args.input_path = util.expand_path(args.input_path)
    args.output_path = util.expand_path(args.output_path)
    return args


def main():
    args = parse_args()

    if os.path.isdir(args.output_path) and not args.force:
        choice = util.query_yes_no("Output path already exists, would you like to override it?", default="no")
    else:
        choice = True

    if choice:
        shutil.rmtree(args.output_path, ignore_errors=True)
        util.mkdir_p(args.output_path)
        util.prep_data_for_training(args.input_path, args.output_path)
    else:
        LOG.info("Remove output path or use --force")


if __name__ == '__main__':
    main()
