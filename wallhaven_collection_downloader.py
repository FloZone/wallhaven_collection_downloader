#!/usr/bin/env python3

from argparse import ArgumentParser
import json
import os
import shutil

import requests

base_url = "https://wallhaven.cc/api/v1/collections"


def download_image(pic_url, out_dir, filename):
    # Create dir
    if not os.path.exists(out_dir):
        os.mkdir(out_dir)
    filename = f"{out_dir}/{filename}"
    response = requests.get(pic_url, stream=True)
    with open(filename, "wb") as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response


def main(api_key, collection_id, username, out_dir):
    current_page = 1
    last_page = 1
    nb_downloaded = 0
    # For each page
    while current_page <= last_page:
        # Get data from page
        full_url = f"{base_url}/{username}/{collection_id}?apikey={api_key}&purity=111&page={current_page}"
        response = requests.get(full_url)
        if response.status_code != 200:
            print(f"Error on {full_url}: {response}")
            break
        print(f"Get data for page {current_page}: ok")

        # Get all images from page
        data = json.loads(response.text)
        pics_data = data["data"]
        for pic in pics_data:
            pic_name = pic["id"]
            pic_url = pic["path"]
            print(f"Downloading {pic_url}")
            download_image(pic_url, out_dir, f"{pic_name}.jpg")
            nb_downloaded = nb_downloaded + 1

        print(f"Page {current_page} of {last_page} done")
        total = data["meta"]["total"]
        print(f"Downloaded {nb_downloaded} of {total} done. Remaining {total - nb_downloaded}")
        current_page = current_page + 1
        last_page = data["meta"]["last_page"]
        del response


if __name__ == "__main__":
    parser = ArgumentParser(description="Download a wallhaven collection.")
    parser.add_argument(
        "-k", "--api-key", dest="api_key", required=True, help="Your API key from your wallhaven account"
    )
    parser.add_argument("-i", "--id", dest="collection_id", required=True, help="The collection ID")
    parser.add_argument("-u", "--username", dest="username", required=True, help="Username of the collection owner")
    parser.add_argument("-o", "--output", dest="out_dir", default="pics", help="Output directory (default: pics)")
    args = parser.parse_args()

    main(args.api_key, args.collection_id, args.username, args.out_dir)
