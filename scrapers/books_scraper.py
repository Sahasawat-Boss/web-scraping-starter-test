"""
books_scraper.py
--------------------------------------------------------------------
ดึงข้อมูลหนังสือจาก books.toscrape.com

เว็บนี้เป็น "static" คือ server ส่ง HTML มาพร้อมข้อมูลเลย
เลยใช้แค่ requests + BeautifulSoup ก็พอ ไม่ต้องเปิด browser จริง

สิ่งที่ดึง: ชื่อหนังสือ, ราคา, เรตติ้ง (ดาว), สถานะ stock, ลิงก์
รองรับ pagination (ไล่ดึงทีละหน้าตามค่า MAX_PAGES ใน config)
--------------------------------------------------------------------
"""

from urllib.parse import urljoin

from bs4 import BeautifulSoup

import config
from utils import fetch, polite_sleep

# แปลงคำเรตติ้งจาก class ของเว็บ ("star-rating Three") เป็นตัวเลข
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def parse_book(article, page_url: str) -> dict:
    """
    รับ element <article class="product_pod"> 1 อัน แล้วดึงข้อมูลออกมาเป็น dict
    แยกฟังก์ชันนี้ออกมาเพื่อให้ test ง่าย และอ่านง่าย
    """
    # ชื่อหนังสือ: อยู่ใน attribute title ของ <a> (ชื่อเต็ม ไม่โดนตัด ...)
    link_tag = article.select_one("h3 a")
    title = link_tag["title"]

    # ทำลิงก์ให้เป็น URL เต็ม (ในหน้าเว็บเป็น relative path)
    relative = link_tag["href"]
    url = urljoin(page_url, relative)

    # ราคา เช่น "£51.77" -> ตัดสัญลักษณ์ออก เก็บเป็น float
    price_text = article.select_one("p.price_color").get_text(strip=True)
    price = float(price_text.replace("£", "").replace("Â", ""))

    # เรตติ้ง: class จะเป็นแบบ "star-rating Three"
    rating_class = article.select_one("p.star-rating")["class"]  # -> ['star-rating', 'Three']
    rating_word = rating_class[1]
    rating = RATING_MAP.get(rating_word, 0)

    # สถานะ stock
    availability = article.select_one("p.instock.availability").get_text(strip=True)

    return {
        "title": title,
        "price_gbp": price,
        "rating": rating,
        "availability": availability,
        "url": url,
    }


def scrape() -> list:
    """
    วนดึงข้อมูลทีละหน้าจนครบ MAX_PAGES แล้ว return list ของ dict
    """
    all_books = []
    # หน้าแรก
    page_url = urljoin(config.BOOKS_BASE_URL, "catalogue/page-1.html")

    for page_num in range(1, config.MAX_PAGES + 1):
        print(f"[books] กำลังดึงหน้า {page_num} ...")
        resp = fetch(page_url)
        soup = BeautifulSoup(resp.text, "lxml")

        # หนังสือแต่ละเล่มอยู่ใน <article class="product_pod">
        articles = soup.select("article.product_pod")
        for article in articles:
            all_books.append(parse_book(article, page_url))

        # หาปุ่ม "next" ถ้าไม่มีแปลว่าหมดหน้าแล้ว
        next_link = soup.select_one("li.next a")
        if not next_link:
            print("[books] ไม่มีหน้าถัดไปแล้ว หยุด")
            break

        # สร้าง URL หน้าถัดไป
        page_url = urljoin(page_url, next_link["href"])
        polite_sleep()  # หน่วงก่อนดึงหน้าถัดไป

    print(f"[books] ดึงมาได้ทั้งหมด {len(all_books)} เล่ม")
    return all_books
