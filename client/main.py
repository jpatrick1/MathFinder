import argparse
import requests
import client.common as common
import multiprocessing as mp
import os
import json
from client._logging import get_logger, configure_logging
from tqdm import tqdm


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


class MathFinderClient(ApiClient):
    DISPLAYED = "displayed"
    EMBEDDED = "embedded"

    def __init__(self, server, base_path=None):
        super().__init__(server, base_path)

    def run_math_finder(self, input_img):
        _, _, _, content_type = get_content_type(input_img)

        with open(input_img, 'rb') as f:
            file_content = f.read()

        multipart_form_data = {
            'input': (input_img, file_content, content_type)
        }

        response = self._post("runMathFinder", files=multipart_form_data, status_code=200)
        return response


class CategoryMap(object):
    def __init__(self, ground_truth_categories, response):
        self.gt_cat_name_to_id = {cat["name"]: cat["id"] for cat in ground_truth_categories}
        self.mf_cat_id_to_name = {cat["id"]: cat["name"] for cat in response["categories"]}
        self.mf_name_to_gt_name = {"displayed": "expr_iso", "embedded": "expr_inline"}

    def __call__(self, mf_category_id):
        return self.gt_cat_name_to_id[self.mf_name_to_gt_name[self.mf_cat_id_to_name[mf_category_id]]]


_GT_DPI = 125
_MF_DPI = 300


def mf_bbox_to_gt_bbox(bbox, gt_per_mf_scale=_GT_DPI/_MF_DPI):
    return [mf_coord * gt_per_mf_scale for mf_coord in bbox]


def _run_math_finder(pargs):
    client, directory, image, gt_categories = pargs
    file_name = image["file_name"].replace(f"dpi{_GT_DPI}", f"dpi{_MF_DPI}")
    input_img = os.path.join(directory, file_name)
    try:
        response = client.run_math_finder(input_img)
    except Exception as e:
        logger.exception(f"Possible server error on {input_img}")
        return []

    cat_map = CategoryMap(gt_categories, response)
    coco_dets = []
    for det in response["detections"]:
        coco_dets.append(
            {
                "image_id": image["id"],
                "category_id": cat_map(det["category_id"]),
                "bbox": mf_bbox_to_gt_bbox(det["bbox"]),
                "score": det["score"]
            }
        )
    return coco_dets


def run_math_finder_on_all(client, directory, ground_truth):
    logger.info("Counting tasks...")
    num_tasks = len(ground_truth["images"])
    with mp.Pool() as p:
        results = []
        pargs_gen = ((client, directory, input_img, ground_truth["categories"]) for input_img in ground_truth["images"])
        for x in tqdm(p.imap_unordered(_run_math_finder, pargs_gen), total=num_tasks):
            results.extend(x)
    return results


def main(args):
    client = MathFinderClient(args.server)
    if os.path.isfile(args.img_file):
        response = client.run_math_finder(args.img_file)
    elif os.path.isdir(args.img_file):
        with open(args.ground_truth, "rb") as f:
            gt = json.load(f)
        response = run_math_finder_on_all(client, args.img_file, gt)
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
                        help="Path to image dir (for batched mode, should be directory the filenames in ``ground_truth`` are relative to).")
    parser.add_argument("--output_file", type=str, required=False, default="cocoish_output.json",
                        help="Location for saving results.")
    parser.add_argument("--ground_truth", type=str, required=True,
                        help="COCO-formatted ground truth file for mapping category and img IDs. Using this implies batched mode.")


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
