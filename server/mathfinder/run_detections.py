#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import pathlib
import mathfinder.util as util
from mathfinder.file_loader import FileLoader
import mathfinder.client as client


def get_detections(image):
    return client.get_detections(image, server_url="http://10.1.2.22/mathfinder")
    # return client.get_detections(image)


image_root = os.path.expandvars("$HOME/code/MathFinder/data/Groundtruth/WithoutLabels/")

file_list = util.natural_sort([p.as_posix() for p in pathlib.Path(image_root).glob("**/*.png")])
files = FileLoader(file_list, apply_composite=[get_detections], skip_read=True, readers=1, workers=18)

for idx, (meta, detections) in enumerate(files):
    image = meta["filename"]
    print(idx, image)
    with open(image + ".json", "w") as fout:
        json.dump(detections, fout)
