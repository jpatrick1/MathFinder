#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import json
import logging
import mathfinder.util as util

LOG = logging.getLogger(__name__)


def get_content_type(filename):
    path, file = os.path.split(filename)
    file, ext = os.path.splitext(file)

    content_type = None
    if ext.lower() in [".jpg", ".jpeg"]:
        content_type = "image/jpeg"
    elif ext.lower() in [".png"]:
        content_type = "image/png"
    elif ext.lower() in [".pdf"]:
        content_type = "application/pdf"
    elif ext.lower() in [".json"]:
        content_type = "application/json"

    return path, file, ext, content_type


def get_detections(image_filename, server_url="http://localhost:9030/api/v1"):
    # following url must return a status_code of 200, the swagger ui page is a good candidate
    session = util.get_session(util.urljoin(server_url, 'ui'))
    url = util.urljoin(server_url, "runMathFinder")
    path, file, ext, content_type = get_content_type(image_filename)

    if content_type:
        with open(image_filename, 'rb') as fin:
            image = fin.read()

        data = None
        files = {
            # 'input': (f"{file}{ext}", image, content_type)

            # TODO, fix in server
            # need to label image starting w/0
            'input': ("0{:s}".format(ext), image, content_type)
        }

        response = session.post(url, data=data, files=files)

        if response.status_code != 200:
            # raise Exception("Error in response request")
            if response.status_code == 504:
                return {"error": "504 Gateway Timeout"}
            else:
                return json.loads(response.text)
    else:
        raise TypeError("Unable to determine content_type from filename")

    return json.loads(response.content.decode("utf-8"))
