#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module contains a parallel/multiprocess FileLoader class
"""
import os
import logging
import time
import queue
import multiprocessing as mp
from enum import Enum


class Event(Enum):
    START = 0
    STOP = 1
    QUIT = 2
    BYTES = 3


LOG = logging.getLogger(__name__)


class FileLoader(object):
    """
    Multiprocessed file loader that gives options to apply function to files read in before adding to generator queue.

    Parameters
    ----------
    file_list : list of str
        List of absolute file paths.
    readers : int, optional
        Number of processes to use for reading files from disk
    apply_composite : list of callable objects, optional
        List of function pointers and/or functors. Each element in list must accept the output from the previous
        function with the first element taking in a file as a byte string.
    workers : int, optional
        Number of processes to use for post-processing, only used if apply_composite is not None
    skip_read : bool, optional
        Skips reading file and passes filename to next function
    kwargs : dict
        Not currently used. Additional arguments that could be passed composite (post-processing) functions.

    Yields
    ------
    object : bytes or TBD
        Type of object is bytes if apply_composite is None, otherwise type is determined by last function in
        apply_composite list
    """
    _SKIP = False

    def __init__(self, file_list, readers=2, apply_composite=None, workers=None, skip_read=False, **kwargs):
        self._timeout = 60
        self._fn_q = mp.Queue()
        self._input_q = mp.Queue(maxsize=500)
        self._worker_q = mp.Queue(maxsize=500)
        self._output_q = mp.Queue(maxsize=5000)
        self._ps = []

        FileLoader._SKIP = skip_read

        # process to build file list queue
        self._ps.append(mp.Process(target=FileLoader._build_filename_queue, args=(self._fn_q, file_list)))

        # file reading processes
        for pid in range(readers):
            self._ps.append(mp.Process(target=FileLoader._file_reader, args=(self._fn_q, self._input_q)))

        if apply_composite is not None:
            if workers is None or workers < 1:
                workers = os.cpu_count()

            for pid in range(workers):
                self._ps.append(
                    mp.Process(target=FileLoader._post_process, args=(self._input_q, self._worker_q, apply_composite)))

            # process to sync output of file reader processes
            self._ps.append(
                mp.Process(target=FileLoader._order_outputs, args=(self._worker_q, self._output_q, self._timeout)))
        else:
            self._ps.append(
                mp.Process(target=FileLoader._order_outputs, args=(self._input_q, self._output_q, self._timeout)))

        for p in self._ps:
            p.start()

    def __del__(self):
        for pid, p in enumerate(self._ps):
            p.join()

    def __iter__(self):
        return self.next()

    def next(self):
        while True:
            try:
                value = self._output_q.get()
            except queue.Empty as e:
                pass
            else:
                if value == Event.QUIT:
                    return
                elif value is not None:
                    yield value

    @staticmethod
    def _post_process(input_q, worker_q, apply_composite):
        p_name = mp.current_process().name
        LOG.debug(p_name)
        if not isinstance(apply_composite, list):
            apply_composite = [apply_composite]

        more = True

        while more:
            try:
                meta, file = input_q.get(block=True, timeout=1)
            except Exception as e:
                more = False
            else:
                for func in apply_composite:
                    if hasattr(func, "us../..es_meta"):
                        meta.file_meta, file = func((meta, file))
                    else:
                        file = func(file)

                worker_q.put((meta, file), block=True, timeout=60)

    @staticmethod
    def _order_outputs(input_q, output_q, timeout=60):
        p_name = mp.current_process().name
        LOG.debug(p_name)
        idx = 0
        more = True
        file_dict = {}

        while more:
            stime = time.time()
            try:
                meta, file = input_q.get(block=False)
            except queue.Empty as e:
                pass
            except Exception as e:
                LOG.debug("idx: {:d}".format(idx))
                more = False
            else:
                file_dict[meta["idx"]] = (meta, file)

            if idx in file_dict:
                value = file_dict.pop(idx)
                LOG.debug((value[0]["idx"], value[0]["filename"]))
                output_q.put(value)
                idx += 1

                if idx == meta["total_files"]:
                    output_q.put(Event.QUIT)
                    more = False

            etime = time.time()
            if (etime - stime) > timeout:
                LOG.error("Timeout reached")
                raise Exception("Timeout reached")

    @staticmethod
    def _build_filename_queue(fn_q, file_list):
        p_name = mp.current_process().name
        LOG.debug(p_name)
        total_files = len(file_list)
        for idx, fn in enumerate(file_list):
            meta = {'idx': idx, 'filename': fn, 'total_files': total_files}
            # LOG.debug((meta.idx, meta.total_files, meta.filename))
            fn_q.put(meta, block=True)

    @staticmethod
    def _file_reader(fn_q, input_q):
        p_name = mp.current_process().name
        LOG.debug(p_name)
        more = True

        while more:
            try:
                meta = fn_q.get(block=True, timeout=1)
            except Exception as e:
                more = False
            else:
                LOG.debug("{:s}: {:d}".format(p_name, meta["idx"]))

                if FileLoader._SKIP:
                    file = meta["filename"]
                else:
                    file = FileLoader.read_file(meta["filename"])

                input_q.put((meta, file), block=True)

    @staticmethod
    def read_file(filename):
        try:
            with open(filename, "rb") as fin:
                file = fin.read()
        except Exception as e:
            # TODO, handle exception
            file = None

        return file
