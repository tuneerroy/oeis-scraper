from bs4 import BeautifulSoup


def get_oeis_links(soup: BeautifulSoup):
    links = soup.findAll("a")
    res = set()
    for link in links:
        if not (href := link.get("href")):
            continue

        if not href.startswith("http://oeis.org"):
            href = "http://oeis.org" + href
        latter = href[len("http://oeis.org/") :]
        if latter.startswith("A") and latter[1:].isdigit():
            res.add(href)
    return list(res)
