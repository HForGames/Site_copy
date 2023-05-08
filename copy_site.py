import argparse
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import os
import json
from pathlib import Path

type_bs = {
    "audio": "src",
    "embed": "src",
    "iframe": "src",
    "img": "src",
    "input": "src",
    "object": "data",
    "source": "src",
    "track": "src",
    "video": "src",
    "link": "href",
    "script": "src"
}

lambda_version = {
    "classic": lambda directory, filename, extension: f"{directory}/{filename}{extension}",
    "jinja": lambda directory, filename,
                    extension: f"{{{{ url_for('static', filename='{directory}/{filename}{extension}') }}}}"
}

with open("mimeType.json", "r") as f:
    mimetypes = json.load(f)


def download(filename, parsed_url, src):
    response = requests.get(src, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
        "origin": f"{parsed_url.scheme}://{parsed_url.netloc}", "referer": f"{parsed_url.scheme}://{parsed_url.netloc}",
        "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "cross-site", "sec-gpc": "1",
        "upgrade-insecure-requests": "1", "cache-control": "max-age=0"})
    if response.status_code != 200:
        print("Not Found :", src)
    try:
        extension = mimetypes[response.headers["Content-Type"].split(";")[0]]
    except KeyError:
        print("Mimetype not found")
        print("Add the mimetype to mimeType.json")
        print("Mime type :", response.headers["Content-Type"].split(";")[0])
        exit()
    directory = extension.split(".")[-1]
    if not os.path.isdir(f"./downloads/{parsed_url.netloc}/{directory}"):
        os.mkdir(f"./downloads/{parsed_url.netloc}/{directory}")
    text = response.content
    with open(f"./downloads/{parsed_url.netloc}/{directory}/{filename}{extension}", "wb") as f:
        f.write(text)
    print("Downloaded :", src)
    return directory, extension, filename


def getting_script(soup, parsed_url, url):
    for script in soup.find_all('script'):
        if script.get("src") is None or script.get("src").startswith("//") or script.get("src") == url:
            continue
        src = script.get("src")
        if not src.startswith("http"):
            src = f"{parsed_url.scheme}://{parsed_url.netloc}/{src}"
        filename = src.split("?")[0].split("/")[-1]
        directory, extension, filename = download(filename, parsed_url, src)
        str_script = str(script)
        start_index = str_script.find("src=") + 5
        new_script = str_script[:start_index] + f"{directory}/{filename}{extension}" + str_script[str_script.find('"', start_index):]
        script.replaceWith(BeautifulSoup(new_script, 'html.parser'))
    return soup


def remove_all(parsed_url):
    for root, dirs, files in os.walk(f"./downloads/{parsed_url.netloc}/", topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(f"./downloads/{parsed_url.netloc}")


def download_and_replace(soup, list_tags, args, parsed_url):
    dict_of_url = {}
    string_soup = str(soup)
    for metatype in list_tags.keys():
        for tag in list_tags[metatype]:
            link = tag.get(type_bs[metatype])
            base_link = link
            if link is None:
                continue
            if link.startswith("//"):
                link = f"{parsed_url.scheme}:{link}"
                filename = link.split("?")[0].split("/")[-1]
            elif link.startswith("/"):
                link = f"{parsed_url.scheme}://{parsed_url.netloc}{link}"
                filename = link.split("?")[0].split("/")[-1]
            elif link.startswith("http"):
                filename = link.split("?")[0].split("/")[-1]
            else:
                link = f"{parsed_url.scheme}://{parsed_url.netloc}/{link}"
                filename = link.split("?")[0].split("/")[-1]
            if link == args.url or filename == "" or not link.startswith("http") or link.startswith(
                    "mailto") or link.startswith("tel"):
                continue
            filename = filename.split(".")[0]
            if link in dict_of_url.keys():
                print(f"Already download : {link}")
                directory, extension, filename = dict_of_url[link]
            else:
                directory, extension, filename = download(filename, parsed_url, link)
                dict_of_url[link] = [directory, extension, filename]
            string_to_change = lambda_version[args.parse_version](directory, filename, extension)
            string_soup = string_soup.replace(f'{type_bs[metatype]}="{base_link}"',
                                              f'{type_bs[metatype]}="{string_to_change}"')
    return BeautifulSoup(string_soup, 'html.parser')


def copy_site(args, parsed_url):
    response = requests.get(args.url)
    response.raise_for_status()
    index = response.text
    soup = BeautifulSoup(index, 'html.parser')
    for script in soup.find_all("noscript"):
        script.decompose()
    soup = download_and_replace(soup,
                                {balise: soup.find_all(balise) for balise in type_bs.keys()},
                                args,
                                parsed_url)
    html = soup.prettify()
    with open(f"./downloads/{parsed_url.netloc}/index.html", "w") as f:
        f.write(html)


def main():
    parser = argparse.ArgumentParser(prog="copy_site.py",
                                     description="Copy a website",
                                     epilog="by default the website is copied in the folder downloads")
    parser.add_argument("-u", "--url", help="url of the website to copy", required=True)
    parser.add_argument("-p", "--parse_version", help="version of the parser", type=str, default="classic",
                        choices=["classic", "jinja"])
    args = parser.parse_args()
    parsed_url = urlparse(args.url)
    if os.path.isdir(f"./downloads/{parsed_url.netloc}"):
        if input("The folder already exist do you want to remove it ? (y/n)") == "y":
            remove_all(parsed_url)
        else:
            exit()
    Path(f"./downloads/{parsed_url.netloc}").mkdir(parents=True, exist_ok=True)
    copy_site(args, parsed_url)


if __name__ == '__main__':
    main()
