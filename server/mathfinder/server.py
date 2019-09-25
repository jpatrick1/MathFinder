#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import argparse
import logging
import connexion
from mathfinder.util import which

LOG = logging.getLogger(__name__)

API = {
    "openapi": "3.0.0",
    "info": {
        "title": "MathFinder",
        "version": "1",
        "description": "HTTP Interface for MathFinder"},
    "paths": {
        "/runMathFinder": {
            "post": {
                "summary": "Returns Rect Information",
                "tags": ["MathFinder"],
                "operationId": "mathfinder.endpoint.math_finder",
                "requestBody": {
                    "content": {
                        "multipart/form-data": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "input": {
                                        "type": "string",
                                        "format": "binary"}},
                                "required": ["input"]}}}},
                "responses": {
                    "200": {
                        "description": "Rect JSON",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {}}}}}}}}}}


def parse_args():
    h = {
        "program": "MathFinder",
        "host": "Host or IP that server is running on",
        "port": "Port number",
        "base-path": "Base path to use in url, e.g. http://host:port/base-path/endpoint",
        "exe-path": "Path to MathFinder"}

    host = os.environ.get("HOST", "0.0.0.0")
    port = os.environ.get("PORT", 9030)
    base_path = os.environ.get("BASEPATH", "/api/v1")

    # test
    # os.environ["PATH"] = "/home/patricja/code/MathFinder/src/FINDER/APP/:" + os.environ["PATH"]
    exe_path = os.environ.get("MATH_FINDER", which('MathFinder'))

    parser = argparse.ArgumentParser(description=h['program'], formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--host', help=h['host'], type=str, default=host)
    parser.add_argument('--port', help=h['port'], type=str, default=port)
    parser.add_argument('--base-path', dest='base_path', help=h['base-path'], type=str, default=base_path)
    parser.add_argument('--exe-path', dest='exe_path', help=h['exe-path'], type=str, default=exe_path)

    args = parser.parse_args()
    os.environ["HOST"] = args.host
    os.environ["PORT"] = str(args.port)
    os.environ["BASEPATH"] = args.base_path
    os.environ["MATH_FINDER"] = args.exe_path
    return args


def main():
    a = parse_args()
    app = connexion.App(__name__)
    curr_path, _ = os.path.split(os.path.realpath(__file__))
    app.add_api(API, base_path=a.base_path)
    app.run(server='tornado', host=a.host, port=a.port)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s][%(module)s:%(funcName)s:%(lineno)d] %(levelname)s - %(message)s')
    main()
