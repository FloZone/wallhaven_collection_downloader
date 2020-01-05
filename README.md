Wallhaven collection downloader
========

A simple script for downloading Wallhaven collections.

## Requirements
- Python >3.6
- requests lib

## How to use
You first need to get your API key from Wallhaven website.
It is located on your account settings: [https://wallhaven.cc/settings/account](https://wallhaven.cc/settings/account).

You also need to get the ID of the collection you want to download and the username of the collection owner. You can get these info from the URL of a collection.\
For exemple: https://wallhaven.cc/user/flozone/favorites/123456 will give you **123456** and **flozone**.

Then, simply run the script with the data as args.

## Command-line help

```
usage: python wallhaven_collection_downloader.py [-h] -k API_KEY -i COLLECTION_ID -u USERNAME [-o OUT_DIR]

Download a wallhaven collection.

optional arguments:
  -h, --help            show this help message and exit
  -k API_KEY, --api-key API_KEY
                        Your API key from your wallhaven account
  -i COLLECTION_ID, --id COLLECTION_ID
                        The collection ID
  -u USERNAME, --username USERNAME
                        Username of the collection owner
  -o OUT_DIR, --output OUT_DIR
                        Output directory (default: pics)
```
