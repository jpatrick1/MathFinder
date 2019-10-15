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
    proc = sp.run(shlex.split(cmd), env=os.environ, stdout=sp.PIPE, stderr=sp.PIPE)
    image_list = util.get_image_list(path, ext=ext, recursive=False)
    image_index = [util.split_fname(f)[1] for f in image_list]
    image_map = {f: i for i, f in enumerate(image_index)}
    images = [{"id": image_map[f], "file_name": f + ext} for f in image_index]

    # add width/height information to images
    for idx, img_fn in enumerate(image_list):
        img = open(img_fn, "rb").read()
        c, w, h = util.get_image_info(img)
        images[idx]["height"] = h
        images[idx]["width"] = w

    if proc.returncode:
        error_msg = proc.stderr.decode("utf-8")
        LOG.debug(error_msg)
        response = {"error_message": error_msg}, 400

    else:
        dets = util.read_rect_file(os.path.join(path, os.path.basename(path), "results.rect"))
        labels = {"displayed": 0, "embedded": 1}
        results = {
            "images": images,
            "categories": [
                {"id": 0, "name": "displayed"},
                {"id": 1, "name": "embedded"}],
            "detections": []}

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


def display_detections(image, detections):
    image_content = image.content_type in ["image/png", "image/jpeg"]
    detection_content = detections.content_type == "application/json"
    if image_content and detection_content:
        overlay = util.display_detections(image, detections)
        response = overlay, 200
    else:
        error_msg = "Invalid content type image: [image/png, image/jpeg] and detections == application/json"
        LOG.debug(error_msg)
        response = {"error_message": error_msg}, 400

    return response


def math_finder(input, body):
    filename = input.filename
    ext = os.path.splitext(filename)[1]

    with tempfile.TemporaryDirectory() as temp_path:
        with open(os.path.join(temp_path, "0" + ext), 'wb') as f:
            f.write(input.stream.read())
        try:
            response = run_math_finder(temp_path, ext)
            response[0]["images"][0]["file_name"] = input.filename
        except Exception as err:
            error_msg = str(err)
            LOG.error(error_msg)
            response = json.dumps({"error_message": error_msg}), 400

    return response


run_math_finder("/home/patricja/code/MathFinder.copy/data/Groundtruth/WithoutLabels/advcalc1", ".png")
