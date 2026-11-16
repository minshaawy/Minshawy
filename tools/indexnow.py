#!/usr/bin/env python3
"""Tell IndexNow search engines (Bing, Yandex, Seznam, Naver…) about every URL
in sitemap.xml. Run after a deploy:

    python3 tools/indexnow.py
"""
import glob
import json
import os
import re
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = "www.elminshawy.net"

keys = [os.path.basename(p)[:-4] for p in glob.glob(os.path.join(ROOT, "*.txt"))
        if re.fullmatch(r"[0-9a-f]{32}", os.path.basename(p)[:-4])]
assert len(keys) == 1, f"expected one IndexNow key file, found {keys}"
key = keys[0]
urls = re.findall(r"<loc>([^<]+)</loc>", open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read())

body = json.dumps({"host": HOST, "key": key, "keyLocation": f"https://{HOST}/{key}.txt", "urlList": urls}).encode()
req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body,
                             headers={"Content-Type": "application/json; charset=utf-8"})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print("IndexNow:", r.status, f"({len(urls)} URLs submitted)")
except urllib.error.HTTPError as e:
    print("IndexNow:", e.code, e.read().decode()[:300])
