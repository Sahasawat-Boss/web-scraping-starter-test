"""
quotes_scraper.py
--------------------------------------------------------------------
ดึงคำคมจาก quotes.toscrape.com

เป็นอีกตัวอย่างของเว็บ static แต่โครงสร้างข้อมูลต่างจากหนังสือ
(1 quote มีหลาย tag -> เก็บเป็น list ซ้อนใน dict)
เอาไว้ดูว่าเวลาข้อมูลซับซ้อนขึ้นนิดนึงจะจัดการยังไง
--------------------------------------------------------------------
"""

from urllib.parse import urljoin

from bs4 import BeautifulSoup

import config
from utils import fetch, polite_sleep


def parse_quote(box) -> dict:
    """รับ <div class="quote"> 1 อัน คืนเป็น dict"""
    text = box.select_one("span.text").get_text(strip=True)
    author = box.select_one("small.author").get_text(strip=True)
    # 1 quote มีได้หลาย tag -> เก็บเป็น list
    tags = [t.get_text(strip=True) for t in box.select("a.tag")]
    return {
        "quote": text,
        "author": author,
        "tags": ", ".join(tags),  # join เป็น string เดียวเพื่อให้เซฟ CSV ง่าย
    }


def scrape() -> list:
    all_quotes = []
    page_url = config.QUOTES_BASE_URL

    for page_num in range(1, config.MAX_PAGES + 1):
        print(f"[quotes] กำลังดึงหน้า {page_num} ...")
        resp = fetch(page_url)
        soup = BeautifulSoup(resp.text, "lxml")

        for box in soup.select("div.quote"):
            all_quotes.append(parse_quote(box))

        next_link = soup.select_one("li.next a")
        if not next_link:
            print("[quotes] ไม่มีหน้าถัดไปแล้ว หยุด")
            break

        page_url = urljoin(page_url, next_link["href"])
        polite_sleep()

    print(f"[quotes] ดึงมาได้ทั้งหมด {len(all_quotes)} quote")
    return all_quotes
