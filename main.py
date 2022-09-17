from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import os
import json

with open("mimeType.json", "r") as f:
    mimetypes = json.load(f)


def download(filename, parsed_url, src):
    print("Downloading :", src)
    response = requests.get(src)
    response.raise_for_status()
    try :
        extension = mimetypes[response.headers["Content-Type"].split(";")[0]]
    except KeyError:
        print("Mimetype not found")
        print("add the mimetype to mimeType.json")
        print("mime type :", response.headers["Content-Type"].split(";")[0])
        exit()
    filename = filename.split(".")[0]
    directory = extension.split(".")[-1]
    if not os.path.isdir(f"./downloads/{parsed_url.netloc}/{directory}"):
        os.mkdir(f"./downloads/{parsed_url.netloc}/{directory}")
    if os.path.exists(f"./downloads/{parsed_url.netloc}/{directory}/{filename}{extension}"):
        filename = filename + "_1"
    with open(f"./downloads/{parsed_url.netloc}/{directory}/{filename}{extension}", "wb") as f:
        f.write(response.content)
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
        new_script = str_script[:start_index] + f"{directory}/{filename}{extension}" + str_script[str_script.find('"',
                                                                                                                  start_index):]
        script.replaceWith(BeautifulSoup(new_script, 'html.parser'))
    return soup


def getting_img(soup, parsed_url, url):
    for img in soup.find_all("img"):
        if img.get("src") is None or img.get("src").startswith("//") or img.get("src") == url:
            continue
        src = img.get("src")
        if not src.startswith("http"):
            src = f"{parsed_url.scheme}://{parsed_url.netloc}/{src}"
        filename = src.split("?")[0].split("/")[-1]
        directory, extension, filename = download(filename, parsed_url, src)
        str_img = str(img)
        start_index = str_img.find("src=") + 5
        new_img = str_img[:start_index] + f"{directory}/{filename}{extension}" + str_img[
                                                                                 str_img.find('"', start_index):]
        img.replaceWith(BeautifulSoup(new_img, 'html.parser'))
    return soup


def getting_link(soup, parsed_url, url):
    for link in soup.find_all("link"):
        if link.get("href") is None or link.get("href").startswith("//") or link.get("href") == url:
            continue
        href = link.get("href")
        if not href.startswith("http"):
            href = f"{parsed_url.scheme}://{parsed_url.netloc}/{href}"
        filename = href.split("?")[0].split("/")[-1]
        directory, extension, filename = download(filename, parsed_url, href)
        str_link = str(link)
        start_index = str_link.find("href=") + 6
        new_link = str_link[:start_index] + f"{directory}/{filename}{extension}" + str_link[
                                                                                   str_link.find('"', start_index):]
        link.replaceWith(BeautifulSoup(new_link, 'html.parser'))
    return soup


def remove_all(parsed_url):
    for root, dirs, files in os.walk(f"./downloads/{parsed_url.netloc}/", topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(f"./downloads/{parsed_url.netloc}")


def main(url):
    if not os.path.isdir("./downloads"):
        os.mkdir("./downloads")
    parsed_url = urlparse(url)
    if not os.path.isdir(f"./downloads/{parsed_url.netloc}"):
        os.mkdir(f"./downloads/{parsed_url.netloc}")
    else:
        print("Folder already exists")
        rm_cond = input("yes or no (y or n) to remove folder : ")
        if rm_cond.lower() == "y" or rm_cond.lower() == "yes":
            remove_all(parsed_url)
            os.mkdir(f"./downloads/{parsed_url.netloc}")
        else:
            print("Folder not removed")
            exit()
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    dict_to_download = {}
    soup = getting_script(soup, parsed_url, url)
    soup = getting_link(soup, parsed_url, url)
    soup = getting_img(soup, parsed_url, url)
    html = soup.prettify()
    with open(f"./downloads/{parsed_url.netloc}/index.html", "w") as f:
        f.write(html)


if __name__ == '__main__':
    url = input("Enter site to copy :")
    main(url)
