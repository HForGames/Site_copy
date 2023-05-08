# Site_Copy

It's a simple tool to copy a website.

## Usage

if you just want to copy a site you just have to do that:

```bash
$ pip install -r requierments.txt
$ python copy_site.py -u https://example.com
```

## Arguments

```bash
$ python copy_site.py -h
usage: copy_site.py [-h] -u URL [-p {classic,jinja}] [-m]

Copy a website

options:
  -h, --help            show this help message and exit
  -u URL, --url URL     url of the website to copy
  -p {classic,jinja}, --parse_version {classic,jinja}
                        version of the parser

by default the website is copied in the folder downloads
```

## Warning

* Issue with mimetype add it to `mimeTypes.json`
* Issue with CORS policy run the index.html with a server
