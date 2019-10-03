import argparse
import requests
import client.common as common
import multiprocessing as mp
import os
import json
from client._logging import get_logger, configure_logging


logger = get_logger(__name__)


class ApiClient:
    def __init__(self, server, base_path):
        self._server = server
        self._base_path = base_path
        self._session = requests.Session()

    def _get(self, endpoint, path_param=None, status_code=200):
        if path_param:
            url = common.join(self._server, self._base_path, endpoint, f"{path_param}")
        else:
            url = common.join(self._server, self._base_path, endpoint)

        response = self._session.get(url)
        if not response.status_code == status_code:
            raise AssertionError(f"Expected code {status_code}, got {response.status_code}")
        return response.json()

    def _post(self, endpoint, status_code=201, **kwargs):
        url = common.join(self._server, self._base_path, endpoint)
        response = self._session.post(url, **kwargs)
        assert response.status_code == status_code, f"Expected code {status_code}, got {response.status_code}"
        return response.json()

    def _put(self, endpoint, status_code=200, **kwargs):
        url = common.join(self._server, self._base_path, endpoint)
        response = self._session.put(url, **kwargs)
        assert response.status_code == status_code, f"Expected code {status_code}, got {response.status_code}"
        return response.json()

    def _delete(self, endpoint, path_param=None, status_code=204, **kwargs):
        if path_param:
            url = common.join(self._server, self._base_path, endpoint, f"{path_param}")
        else:
            url = common.join(self._server, self._base_path, endpoint)

        response = self._session.delete(url, **kwargs)
        assert response.status_code == status_code, f"Expected code {status_code}, got {response.status_code}"
        return True


class MathFinderClient(ApiClient):
    def __init__(self, server, base_path=None):
        super().__init__(server, base_path)

    def run_math_finder(self, input_img):
        logger.info(f"Running MathFinder on {input_img}")
        with open(input_img, 'rb') as f:
            file_content = f.read()

        multipart_form_data = {
            'input': file_content,
        }

        response = self._post("runMathFinder", files=multipart_form_data, status_code=200)
        assert len(response["images"]) == 1
        response["images"][0]["file_name"] = input_img
        return response


def _run_math_finder(pargs):
    client, input_img = pargs
    return client.run_math_finder(input_img)


def list_imgs(directory):
    for root, dirs, files in os.walk(directory):
        for filename in files:
            if not filename.endswith(".png"):
                continue
            file_path = os.path.join(root, filename)
            yield file_path


def list_of_results_to_cocoish(list_of_results):
    assert all((list_of_results[0]["categories"] == other_result["categories"]
               for other_result in list_of_results[1:]))
    cocoish = {
        "categories": list_of_results[0]["categories"],
        "images": [],
        "detections": []
    }

    for new_id, result in enumerate(list_of_results):
        assert len(result["images"]) == 1
        img = result["images"][0]
        img["id"] = new_id
        cocoish["images"].append(img)
        for ann in result["detections"]:
            ann["area"] = ann["bbox"][2] * ann["bbox"][3]
            ann["image_id"] = new_id
            cocoish["detections"].append(ann)
    return cocoish


def run_math_finder_on_all(client, directory):
    with mp.Pool() as p:
        results = p.map(_run_math_finder,
            ((client, input_img) for input_img in list_imgs(directory))
        )
    cocoish_results = list_of_results_to_cocoish(results)
    return cocoish_results


def main(args):
    client = MathFinderClient(args.server)
    if os.path.isfile(args.img_file):
        response = client.run_math_finder(args.img_file)
    elif os.path.isdir(args.img_file):
        response = run_math_finder_on_all(client, args.img_file)
    else:
        raise FileNotFoundError()

    with open(args.output_file, "w") as f:
        json.dump(response, f)


def _add_args(parser):
    """Add arguments to parser.

    Parameters
    ----------
    parser : argparse.ArgumentParser

    """
    parser.add_argument("--server", type=str, default="http://10.1.2.22/mathfinder",
                        help="Path to COCO-formatted predictions file.")
    parser.add_argument("--img_file", type=str, required=True,
                        help="Path to image file or dir.")
    parser.add_argument("--output_file", type=str, required=False, default="output.json",
                        help="Location for saving results.")


def _get_parser():
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    _add_args(parser)
    return parser


def _parse_args():
    parser = _get_parser()
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    _args = _parse_args()
    configure_logging()
    main(_args)
