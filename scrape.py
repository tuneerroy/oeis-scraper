import json
import os
import sys
from typing import List

import requests
from bs4 import BeautifulSoup


def get_core_sequence_links() -> List[str]:
    domain = "http://oeis.org"
    url = f"{domain}/wiki/Index_to_OEIS:_Section_Cor#core"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    links = set()
    for link in soup.findAll("a"):
        if not (href := link.get("href")):
            continue

        if href.startswith(domain):
            if "/" not in href[len(domain) + 1 :]:
                links.add(href)
    return list(links)


if __name__ == "__main__":
    overwrite = sys.argv[1] == "--overwrite" if len(sys.argv) > 1 else False

    if not overwrite:
        if os.path.exists("data/list.json"):
            raise FileExistsError("data/list.json already exists")

    links = get_core_sequence_links()
    data = [
        {
            "link": link,
            "name": link.split("/")[-1],
            "scraped": False,
        }
        for link in links
    ]
    with open("data/list.json", "w") as f:
        json.dump(data, f, indent=4)
