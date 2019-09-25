#!/usr/bin/env python
# -*- coding: utf-8 -*-

API = {
	"openapi": "3.0.0",
	"info": {
		"title": "MathFinder",
		"version": "1",
		"description": "HTTP Interface for MathFinder"
	},
	"paths": {
		"/runMathFinder": {
			"post": {
				"summary": "Returns Rect Information",
				"tags": [
					"MathFinder"
				],
				"operationId": "mathfinder.endpoint.math_finder",
				"requestBody": {
					"content": {
						"multipart/form-data": {
							"schema": {
								"type": "object",
								"properties": {
									"input": {
										"type": "string",
										"format": "binary"
									}
								},
								"required": [
									"input"
								]
							}
						}
					}
				},
				"responses": {
					"200": {
						"description": "Rect JSON",
						"content": {
							"application/json": {
								"schema": {
									"type": "object",
									"properties": {}
								}
							}
						}
					}
				}
			}
		},
		"/displayDetections": {
			"post": {
				"summary": "Returns image with detections overlayed",
				"tags": [
					"MathFinder"
				],
				"operationId": "mathfinder.endpoint.display_detections",
				"requestBody": {
					"content": {
						"multipart/form-data": {
							"schema": {
								"type": "object",
								"properties": {
									"image": {
										"type": "string",
										"format": "binary"
									},
									"detections": {
										"type": "string",
										"format": "binary"
									}
								},
								"required": [
									"image",
									"detections"
								]
							},
							"encoding": {
								"detections": {
									"contentType": "application/json"
								},
								"image": {
									"contentType": "image/png, image/jpeg"
								}
							}
						}
					}
				},
				"responses": {
					"200": {
						"description": "Image",
						"content": {
							"image/jpeg": {
								"schema": {
									"type": "string",
									"format": "binary"
								}
							}
						}
					}
				}
			}
		}
	}
}