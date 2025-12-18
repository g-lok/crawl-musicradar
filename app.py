import re
import argparse
import pprint
import subprocess

import requests
from bs4 import BeautifulSoup
import validators


def find_links(url):
    # Fetch the content from the URL
    url_response = requests.get(url)
    html_content = url_response.content
    soup = BeautifulSoup(html_content, "html.parser")
    links = soup.find_all("a", href=True)
    return links


def get_url_file_name(url):
    match = re.search(r"(?<=/)[^/\\\\?#]+(?=[^/]*$)", url)
    return match.group(0)


def download_zip(url, download_location):
    filename = get_url_file_name(url)
    full_dl_path = f"{download_location}{filename}"
    print(f"full dl path: {full_dl_path}")

    # Using wget because requests and curl failed me.
    wget = subprocess.call(["wget", "--continue", "-P", download_location, url])

    if wget == 0:
        print(f"Wget executed: {url}")
    else:
        print(f"Wget did not execute. {url}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--site_url", type=str, help="Web site to scrape")
    parser.add_argument(
        "--download_folder", type=str, help="Where to download the files"
    )

    args = parser.parse_args()

    link_pile = find_links(args.site_url)
    first_urls = []
    for link in link_pile:
        href = link["href"]
        valid = validators.url(href)
        if valid and "sample" in href:
            first_urls.append(href)
    pprint.pprint(f"first_urls: {first_urls}")

    zip_hrefs = []
    for url in first_urls:
        child_urls = find_links(url)
        for child_url in child_urls:
            child_href = child_url["href"]
            valid = validators.url(child_href)
            if valid and "zip" in child_href:
                zip_hrefs.append(child_href)
    pprint.pprint(zip_hrefs)

    zip_set = set(zip_hrefs)
    for zip_href in zip_set:
        download_zip(zip_href, args.download_folder)


if __name__ == "__main__":
    main()
