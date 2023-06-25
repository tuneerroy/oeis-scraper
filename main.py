import asyncio
import json
import os
from typing import Set
import aiohttp
from bs4 import BeautifulSoup

from utils import get_oeis_links

RATE_LIMITER = asyncio.Semaphore(100)


async def get_site_content(link: str) -> BeautifulSoup:
    async with RATE_LIMITER:
        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                return await response.text()


def get_sequence(soup):
    sequence_elem = soup.find("tt")
    sequence_text = sequence_elem.get_text().replace(",", "").strip()
    sequence = [int(num) for num in sequence_text.split()]
    return sequence


def get_description(soup):
    return lines_with_more_than_k_words(
        2, soup.find("td", {"align": "left", "valign": "top"}).text.strip()
    )


def lines_with_more_than_k_words(k, text):
    lines = text.split("\n")
    filtered_lines = [line for line in lines if len(line.split()) > k]
    result = "\n".join(filtered_lines)
    return result.strip()


def get_keywords(soup):
    keywords_div = soup.find("div", {"class": "Seq SeqK"})
    keywords_text = keywords_div.text.strip().split(",")
    return keywords_text


def get_references(soup):
    references = soup.find_all("div", {"class": "SeqD"})
    return [ref.get_text().strip() for ref in references]


def get_links_section_items(soup):
    links_section = soup.find_all("div", {"class": "Seq SeqH"})
    links_list = []

    for link_div in links_section:
        tt_tags = link_div.find_all("tt")
        for tt_tag in tt_tags:
            tt_text = tt_tag.text.strip()
            link_tag = tt_tag.find("a")

            if link_tag:
                link_text = link_tag.text
                link_url = link_tag["href"]
                links_list.append((tt_text, link_url))
            else:
                links_list.append((tt_text, None))
    return links_list


def get_crossrefs(soup):
    seqy_elements = soup.find_all("div", {"class": "Seq SeqY"})
    crossrefs = []
    for seqy in seqy_elements:
        crossref_text = seqy.get_text(strip=True)
        crossref_links = []
        for link in seqy.find_all("a"):
            crossref_links.append("https://oeis.org" + link["href"])
        crossrefs.append((crossref_text, crossref_links))
    return crossrefs


def get_comments(soup):
    comments_divs = soup.find_all("div", {"class": "SeqC"})
    comments = [comment_div.text.strip() for comment_div in comments_divs]
    return comments


def get_mathematica(soup):
    mathematica_elements = soup.find_all("div", {"class": "Seq Seqt"})
    mathematica_programs = []
    for i, element in enumerate(mathematica_elements, start=1):
        mathematica_programs.append(element.get_text().strip())
    return mathematica_programs


def get_formulas(soup):
    mathematica_elements = soup.find_all("div", {"class": "Seq SeqF"})
    mathematica_programs = []
    for i, element in enumerate(mathematica_elements, start=1):
        mathematica_programs.append(element.get_text().strip())
    return mathematica_programs


def get_programs(soup):
    mathematica_elements = soup.find_all("div", {"class": "Seq Seqo"})
    mathematica_programs = []
    for i, element in enumerate(mathematica_elements, start=1):
        mathematica_programs.append(element.get_text().strip())
    return mathematica_programs


def get_maple(soup):
    mathematica_elements = soup.find_all("div", {"class": "Seq Seqp"})
    mathematica_programs = []
    for i, element in enumerate(mathematica_elements, start=1):
        mathematica_programs.append(element.get_text().strip())
    return mathematica_programs


def compile_data(soup):
    return {
        "sequence": get_sequence(soup),
        "description": get_description(soup),
        "keywords": get_keywords(soup),
        "references": get_references(soup),
        "links": get_links_section_items(soup),
        "crossrefs": get_crossrefs(soup),
        "comments": get_comments(soup),
        "formulas": get_formulas(soup),
        "mathematica": get_mathematica(soup),
        "programs": get_programs(soup),
        "maple": get_maple(soup),
    }


async def scrape_item(link: str, link_list: Set[str]):
    id = link.split("/")[-1]
    if os.path.exists(f"data/{id}.json"):
        return

    content = await get_site_content(link)
    soup = BeautifulSoup(content, "html.parser")

    data = compile_data(soup)
    data["link"] = link

    more_links = get_oeis_links(soup)
    link_list.update(more_links)

    with open(f"data/{id}.json", "w") as f:
        json.dump(data, f)


async def main(link_list: Set[str]):
    c = 0

    async def dangerously_safe_wrapper(f, link, link_list):
        nonlocal c
        try:
            await f(link, link_list)
            c += 1
        except Exception as e:
            print(f"Error with {link}")
            print(e)
            pass
        print("Succeeded [%d]\r" % c, end="")

    curr_list = set()
    while curr_list != link_list:
        diff = link_list - curr_list
        curr_list = link_list.copy()
        tasks = [
            asyncio.create_task(dangerously_safe_wrapper(scrape_item, link, link_list))
            for link in diff
        ]

        await asyncio.gather(*tasks)

        with open("list.json", "w") as f:
            json.dump(list(link_list), f)


def get_list():
    if not os.path.exists("list.json"):
        raise FileNotFoundError("data/list.json not found")

    with open("list.json", "r") as f:
        return json.load(f)


if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)
    link_list = get_list()
    asyncio.run(main(set(link_list)))
