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
import json
import logging
import tempfile
import subprocess as sp
import shlex
import mathfinder.util as util

LOG = logging.getLogger(__name__)


def run_math_finder(path, ext, display=False):
    cmd = 'bash -c "cd {path} && $MATH_FINDER {path}"'.format(path=path)
    # proc = sp.run(shlex.split(cmd), env=os.environ, capture_output=True)
    proc = sp.run(shlex.split(cmd), env=os.environ, stdout=sp.PIPE, stderr=sp.PIPE)

    if proc.returncode:
        error_msg = proc.stderr.decode("utf-8")
        LOG.debug(error_msg)
        response = {"error_message": error_msg}, 400

    else:
        dets = util.read_rect_file(os.path.join(path, os.path.basename(path), "results.rect"))
        labels = {"displayed": 0, "embedded": 1}
        results = {
            "images": [],
            "categories": [
                {"id": 0, "name": "displayed"},
                {"id": 1, "name": "embedded"}],
            "detections": []}

        image_index = sorted(list(set([d[0] for d in dets])))
        image_map = {f: i for i, f in enumerate(image_index)}
        results["images"] = [{"id": image_map[f], "file_name": f + ext} for f in image_index]
        for img, lbl, x1, y1, x2, y2 in dets:
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            det = {
                'image_id': image_map[img],
                'category_id': labels[lbl],
                'bbox': [x1, y1, x2 - x1, y2 - y1],
                'score': 1.0
            }
            results["detections"].append(det)

        LOG.debug(proc.stdout.decode("utf-8"))
        response = results, 200

        if display:
            util.display_detections(path, results)

    return response


def display_detections(image, body):
    util.display_detections(image, body)


def math_finder(input, body):
    if hasattr(input, "filename"):
        filename = input.filename
        ext = os.path.splitext(filename)[1]

    with tempfile.TemporaryDirectory() as temp_path:
        filename = os.path.join(temp_path, filename)
        with open(filename, 'wb') as f:
            f.write(input.stream.read())
        try:
            response = run_math_finder(temp_path, ext)
        except Exception as err:
            error_msg = str(err)
            LOG.error(error_msg)
            response = json.dumps({"error_message": error_msg}), 400

    return response
