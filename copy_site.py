from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import os
import json
import random
import string
import sys
import cssutils

with open("mimeType.json", "r") as f:
    mimetypes = json.load(f)


def random_filename():
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(10))


def download(filename, parsed_url, src):
    print("Downloading :", src)
    response = requests.get(src, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36",
        "origin": f"{parsed_url.scheme}://{parsed_url.netloc}", "referer": f"{parsed_url.scheme}://{parsed_url.netloc}",
        "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "cross-site", "sec-gpc": "1",
        "upgrade-insecure-requests": "1", "cache-control": "max-age=0"})
    if response.status_code == 404:
        print("File not found")
    try:
        extension = mimetypes[response.headers["Content-Type"].split(";")[0]]
    except KeyError:
        print("Mimetype not found")
        print("add the mimetype to mimeType.json")
        print("mime type :", response.headers["Content-Type"].split(";")[0])
        exit()
    directory = extension.split(".")[-1]
    if not os.path.isdir(f"./downloads/{parsed_url.netloc}/{directory}"):
        os.mkdir(f"./downloads/{parsed_url.netloc}/{directory}")
    text = response.content
    with open(f"./downloads/{parsed_url.netloc}/{directory}/{filename}{extension}", "wb") as f:
        f.write(text)
    return directory, extension, filename


dict_of_type = {
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
        new_script = str_script[:start_index] + f"{directory}/{filename}{extension}" + str_script[str_script.find('"',
                                                                                                                  start_index):]
        script.replaceWith(BeautifulSoup(new_script, 'html.parser'))
    return soup


def getting_allBaliseWithPossibleLinks(soup):
    return {balise: soup.find_all(balise) for balise in dict_of_type.keys()}


def remove_all(parsed_url):
    for root, dirs, files in os.walk(f"./downloads/{parsed_url.netloc}/", topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(f"./downloads/{parsed_url.netloc}")


def passing_all_style_to_one_file(soup, parsed_url, parse_version):
    styles = ""
    for style in soup.find_all("style"):
        styles += "\n" + style.get_text()
        style.decompose()
    soup.head.append(BeautifulSoup(f"<link></link>", "html.parser"))


def minify_all(url, parse_version, parsed_url):
    with open(f"./downloads/{parsed_url.netloc}/index.html", "r") as f:
        html = f.read()
    soup = BeautifulSoup(html, 'html.parser')
    passing_all_style_to_one_file(soup, parsed_url, parse_version)


def download_and_replace(list_of_balise, parse_version, parsed_url, url):
    dict_of_url = {}
    for type in list_of_balise.keys():
        for balise in list_of_balise[type]:
            link = balise.get(dict_of_type[type])
            filename = ""
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
            if link == url or filename == "" or not link.startswith("http") or link.startswith(
                    "mailto") or link.startswith(
                "tel"):
                continue
            filename = filename.split(".")[0]
            if link in dict_of_url.keys():
                directory, extension, filename = dict_of_url[link]
            else:
                directory, extension, filename = download(filename, parsed_url, link)
                dict_of_url[link] = [directory, extension, filename]
            str_balise = str(balise)
            start_index = str_balise.find(f"{dict_of_type[type]}=") + len(f"{dict_of_type[type]}=") + 1
            if parse_version == 1:
                string_to_change = f"{directory}/{filename}{extension}"
            else:
                string_to_change = f"{{{{ url_for('static', filename='{directory}/{filename}{extension}') }}}}"
            new_balise = str_balise[:start_index] + string_to_change + str_balise[str_balise.find('"', start_index):]
            balise.replaceWith(BeautifulSoup(new_balise, 'html.parser'))


def parse_argv():
    if "-u" in sys.argv[1:] and sys.argv.index("-u") + 1 < len(sys.argv):
        url = sys.argv[sys.argv.index("-u") + 1]
    else:
        url = input("Enter site to copy :")
    if not os.path.isdir("./downloads"):
        os.mkdir("./downloads")
    parsed_url = urlparse(url)
    if not os.path.isdir(f"./downloads/{parsed_url.netloc}"):
        os.mkdir(f"./downloads/{parsed_url.netloc}")
    else:
        pass
        # if "-r" in sys.argv:
        #     remove_all(parsed_url)
        #     os.mkdir(f"./downloads/{parsed_url.netloc}")
        # else:
        #     print("Folder already exists")
        #     rm_cond = input("yes or no (y or n) to remove folder : ")
        #     if rm_cond.lower() == "y" or rm_cond.lower() == "yes":
        #         remove_all(parsed_url)
        #         os.mkdir(f"./downloads/{parsed_url.netloc}")
        #     else:
        #         print("Folder not removed")
        #         exit()
    if "--classic" in sys.argv:
        parse_version = 1
    elif "--flask" in sys.argv:
        parse_version = 2
    else:
        parse_version = int(input("Choose between replacer\n1 classic\n2 flask\n: "))
        if parse_version != 1 and parse_version != 2:
            exit()
    return url, parse_version, parsed_url, "--minify" in sys.argv


def copy_site(url, parse_version, parsed_url, minify):
    response = requests.get(url)
    response.raise_for_status()
    index = response.text
    soup = BeautifulSoup(index, 'html.parser')
    list_of_balise = getting_allBaliseWithPossibleLinks(soup)
    if not minify:
        download_and_replace(list_of_balise, parse_version, parsed_url, url)
        html = soup.prettify()
        with open(f"./downloads/{parsed_url.netloc}/index.html", "w") as f:
            f.write(html)
    if minify:
        minify_all(url, parse_version, parsed_url)


if __name__ == '__main__':
    copy_site(*parse_argv())
