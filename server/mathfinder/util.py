#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utility code to work with MathFinder

Attributes
----------
LOG : logging.Logger
    Module logger
"""
import os
import io
import json
import sys
import re
import errno
import logging
import pathlib
import hashlib
from PIL import Image, ImageDraw, ImageFont

LOG = logging.getLogger(__name__)


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".

    References
    ----------
    https://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input
    http://code.activestate.com/recipes/577058/
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def natural_sort(string_list):
    """
    Does natural sort on given list

    Parameters
    ----------
    string_list : iter:`str`

    Returns
    -------
    sorted_list : iter:`str`
        List of sorted strings
    """

    def alphanum_key(s):
        """ Turn a string into a list of string and number chunks.
            "z23a" -> ["z", 23, "a"]
        """

        def tryint(s):
            try:
                return int(s)
            except:
                return s

        return [tryint(c) for c in re.split('([0-9]+)', s)]

    return sorted(string_list, key=alphanum_key)


def expand_path(path):
    """
    Expands given path string if it contains env vars e.g. $CODE or ~ for home.

    Parameters
    ----------
    path : str
        Path string

    Returns
    -------
    expanded_path : str
        Expanded path string
    """
    '''Function expands path that uses environment variables and user ~/'''
    return os.path.expanduser(os.path.expandvars(path))


def split_fname(fname):
    """
    Splits full filename into path, filename, ext

    Parameters
    ----------
    fname : str
        Fullpath to file.

    Returns
    -------
    path : str
        Path string without file
    file : str
        File string without extension
    ext : ext
        Extension only
    """
    path, file = os.path.split(expand_path(fname))
    file, ext = os.path.splitext(file)
    return path, file, ext


def create_symlinks(file_list, dst_path, format_specifier=None, start_index=0):
    """
    Creates symbolic linkgs

    Parameters
    ----------
    file_list : str
        Source list of filenames
    dst_path : str
        Destination path to save links
    format_specifier : str, optional
        Python string format specifier that will take an integer based on index of file in list
    start_index : int, optional
        Starting index to use if format specifier is not None
    Returns
    -------
    None
    """
    for idx, file in enumerate(file_list, start=start_index):
        src_path, fn, ext = split_fname(expand_path(file))
        dst_path = os.path.normpath(expand_path(dst_path))
        mkdir_p(dst_path)
        os.chdir(dst_path)
        src = os.path.normpath(src_path)
        rel_path = os.path.relpath(src, dst_path)
        src = os.path.join(rel_path, fn + ext)
        dst = "{:s}{:s}".format(format_specifier, ext).format(idx) if format_specifier else fn + ext
        os.symlink(src, dst)


def mkdir_p(path):
    """
    Creates all directories in the given path.

    Parameters
    ----------
    path : str
        Path string

    Returns
    -------
    None

    Raises
    ------
    OSError
    """
    if os.path.isdir(path):
        return

    if not os.path.isabs(path):
        path = os.path.abspath(path)

    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

    return path


def prep_data_for_training(image_path, output_path):
    """
    Combines multiple folders for training

    Parameters
    ----------
    image_path : str
        Root path of images, recursively combines all folders with images that contain a .rect file
    output_path : str
        Combined output path
    """
    start_index = 0
    all_rects = []
    for rect_file in pathlib.Path(image_path).glob("**/*.rect"):
        LOG.info("Parsing: {:s}".format(str(rect_file)))
        rects = read_rect_file(rect_file)
        dir = rect_file.parent
        image_list = natural_sort(list(set([os.path.join(dir, r[0]) for r in rects])))

        # generate new filenames
        symlink_fns = {split_fname(p)[1]: str(i) for i, p in enumerate(image_list, start=start_index)}

        new_rects = []
        for r in rects:
            fn, ext = split_fname(r[0])[1:]
            new_rects.append([symlink_fns[fn] + ext] + r[1:])

        all_rects.extend(new_rects)

        create_symlinks(image_list, output_path, format_specifier="{:d}", start_index=start_index)
        start_index += len(image_list)

    with open(os.path.join(output_path, "groundtruth.rect"), 'w') as fout:
        fout.write("\n".join([' '.join(r) for r in all_rects]))
        fout.write("\n")


def read_rect_file(rect_file):
    """
    Parses MathFinder .rect file

    Parameters
    ----------
    rect_file : str
        Path to .rect file

    Returns
    -------
    list[list[str]]
        [image label x1 y1 x2 y2]
    """
    rects = []
    with open(rect_file, 'r') as fin:
        for line in fin:
            rects.append(line.strip().split())

    return rects


def which(program):
    """
    Finds location of executable, mimics UNIX 'which'

    Parameters
    ----------
    program : str
        Name of executable to search for

    Returns
    -------
    {str, None}
        Path to executable or None if it is not found

    References
    ----------
    https://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
    """

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def get_checksum(filename=None, xtra_str=None, hasher="sha256", ashex=True):
    """
    Returns checksum of a file and/or string

    Parameters
    ----------
    filename : str, optional
        Fullpath to file

    xtra_str : str, optional
        Any arbitrary string
    hasher : hashlib.method
        Hashlib secure hash algorithm, defaults to sha256
    ashex
        Flag that indicates whether to return the has as a hex string

    Returns
    -------
    hash : str
        Encoded/hashed string
    """
    if hasher == "sha256":
        hasher = hashlib.sha256()
    elif hasher == "md5":
        hasher = hashlib.md5()

    if isinstance(filename, str):
        for block in file_chunk_generator(filename):
            hasher.update(block)
    elif isinstance(filename, bytes):
        hasher.update(filename)
    elif isinstance(filename, memoryview):
        hasher.update(bytes(filename))

    if xtra_str is not None:
        hasher.update(xtra_str)

    hash = hasher.hexdigest() if ashex else hasher.digest()
    return hash


def file_chunk_generator(filename, block_size=65536):
    """
    Chunks file on read and returns in a generator.

    Parameters
    ----------
    filename : str
        Filename
    block_size : str
        Size in bytes of the chunks

    Yields
    ------
    block : bytes
        Block of bytes
    """
    filename = expand_path(filename)
    with open(filename, 'rb') as fid:
        while True:
            block = fid.read(block_size)
            if len(block):
                yield block
            else:
                break


def display_detections(image, detections):
    """
    Displays results object from run_math_finder

    Parameters
    ----------
    image : fobj
        file object for image
    detections : fobj
        Results object in coco format

    Returns
    -------
    bytes
        Jpeg image overlay as bytes file
    """
    dets = json.load(detections)
    overlay = Image.open(image).convert('RGB')
    pen = ImageDraw.Draw(overlay)
    for img_info in dets["images"]:
        id = img_info["id"]
        if image.filename == img_info["file_name"]:
            for d in dets["detections"]:
                if id == d["image_id"]:
                    x, y, w, h = d["bbox"]
                    color = "blue" if d["category_id"] else 'red'
                    pen.rectangle(xy=[x, y, x + w, y + h], outline=color, width=4)

    mem_img = io.BytesIO()
    overlay.save(mem_img, format="jpeg")
    return mem_img.getvalue()
