# -*- coding: utf-8 -*-


import requests
from bs4 import BeautifulSoup
import json
import sys
import re
import time

reload(sys)
sys.setdefaultencoding("utf-8")


def ParseTr(tr):
    tds = tr.select("td")

    icon_idx = 0
    for idx in xrange(0, len(tds)):
        if len(tds[idx].select("span")) == 1:
            icon_idx = idx
            break

    no_td = tds[icon_idx - 1]
    wiki_td = tds[icon_idx + 1]
    no = no_td.get_text().strip()
    name = wiki_td.select("a")[0].get_text()
    url = wiki_td.select("a")[0].get("href")

    return no, name, url


def GenDocFile(no, name, url, doc_file_path):
    fo = open(doc_file_path, "w")

    response = requests.get("https://wiki.52poke.com/{}".format(url))
    response.enconding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")
    content_node = (
        soup.body.select(".mw-body")[0]
        .select("#bodyContent")[0]
        .select("#mw-content-text")[0]
        .select(".mw-parser-output")[0]
    )

    out_content = ""
    c = content_node.select(".mw-headline")[0].parent.next_sibling
    while True:
        out_content += unicode(c)

        c = c.next_sibling
        if c.name == "h2":
            break

    out_content = re.sub(r"href[=\\\"/a-zA-Z%0-9_]+", "", out_content)
    # out_content = re.sub(r"</a>", "</span>", out_content)
    # out_content = re.sub(r"<a.*>", "<span>", out_content)
    out_content = re.sub(r"id[=\\\"/a-zA-Z%0-9_]+", "", out_content)
    out_content = re.sub(r"class[=\\\"/a-zA-Z%0-9_]+", "", out_content)

    fo.write(
        '<body><div class="img-box" style="float:right;"><img src="./img/{}.png" width="200" height="200"></div><h1>{}</h1>{}</body>'.format(
            no, name, out_content
        )
    )
    fo.close()


def DownImg(no):
    response = requests.get("https://cn.portal-pokemon.com/play/pokedex/{}".format(no))
    response.enconding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")

    img_url = "https://cn.portal-pokemon.com"
    img_url += soup.body.select(".pokemon-img__front")[0].get("src")

    #time.sleep(1)

    img = requests.get(img_url)
    fo = open("./doc/img/{}.png".format(no), "wb")
    fo.write(img.content)
    fo.close()

response = requests.get(
    "https://wiki.52poke.com/wiki/%E5%AE%9D%E5%8F%AF%E6%A2%A6%E5%88%97%E8%A1%A8%EF%BC%88%E6%8C%89%E5%85%A8%E5%9B%BD%E5%9B%BE%E9%89%B4%E7%BC%96%E5%8F%B7%EF%BC%89"
)
response.enconding = "utf-8"

soup = BeautifulSoup(response.text, "html.parser")

body_tag = soup.body
eplist = (
    body_tag.select(".mw-body")[0]
    .select("#bodyContent")[0]
    .select("#mw-content-text")[0]
    .select(".mw-parser-output")[0]
    .select(".eplist")
)

indexes = []

for ep in eplist:
    trs = ep.tbody.select("tr")
    for idx in xrange(2, len(trs)):
        no, name, url = ParseTr(trs[idx])
        title = no + " " + name

        print("{} start downloading".format(title))

        doc_file_path = "./doc/{}.html".format(no[1:])
        GenDocFile(no[1:], name, url, doc_file_path)
        DownImg(no[1:])
        
        indexes.append({"t": title, "d": "", "p": doc_file_path})
        print("{} done".format(title))

        time.sleep(1)

indexes_json = json.dumps(indexes)
fo = open("indexes.json", "w")
fo.write(indexes_json)
fo.close()
