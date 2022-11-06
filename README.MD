# Site_Copy

it's a simple site copy tool, it can copy a site.

## Usage

if you just want to copy a site you just have to do that:

```bash
$ pip install -r requierments.txt
$ python copy_site.py
```

## Arguments


| args                      | definition                                                      |
|---------------------------|-----------------------------------------------------------------|
| `-u "https://google.com"` | it's the url of the site you want's to copy                     |
| `-r`                      | it's delete automatically if needed the already store copy site |
| `--flask or --classic`    | it's for parsed version classic or flask                        |
| `--minify`   | it's for minify the css with removing unused class              |
## Warning

* Issue with mimetype add it to `mimeTypes.json`
* Issue with CORS policy run the index.html with a server
