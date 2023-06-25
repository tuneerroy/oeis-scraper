import json
import os
import sys
from typing import List

import requests
from bs4 import BeautifulSoup

from utils import get_oeis_links


def get_core_sequence_links() -> List[str]:
    domain = "http://oeis.org"
    url = f"{domain}/wiki/Index_to_OEIS:_Section_Cor#core"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    return get_oeis_links(soup)


if __name__ == "__main__":
    overwrite = sys.argv[1] == "--overwrite" if len(sys.argv) > 1 else False

    if not overwrite:
        if os.path.exists("list.json"):
            raise FileExistsError("list.json already exists")

    links = get_core_sequence_links()
    with open("list.json", "w") as f:
        json.dump(links, f, indent=4)
