"""
app.py — เว็บแอปสำหรับ scrape เว็บ "ไหนก็ได้" ผ่านหน้าเว็บ
--------------------------------------------------------------------
วิธีใช้:
    python app.py
แล้วเปิดเบราว์เซอร์ไปที่  http://127.0.0.1:5000

- แปะ URL ในช่อง แล้วกด "ดึงข้อมูล"
- ไม่ใส่ selector = โหมดอัตโนมัติ (ดึง หัวข้อ/ลิงก์/รูป/ตาราง/ย่อหน้า มาให้)
- ใส่ CSS selector = เจาะจงเลือกเฉพาะ element ที่ต้องการ
--------------------------------------------------------------------
ทำไมต้องมี server ตัวนี้:
    เบราว์เซอร์ scrape เว็บอื่นตรง ๆ ไม่ได้ (ติด CORS)
    server ตัวนี้เลยเป็นคนไป fetch HTML ให้ แล้วส่งข้อมูลกลับไปโชว์บนหน้าเว็บ
"""

import os

# เครื่องนี้ตั้ง env ของ mitmproxy ค้างไว้ (REQUESTS_CA_BUNDLE / SSL_CERT_FILE)
# ทำให้ SSL verify พังตอนต่อเว็บตรง ๆ -> เอาออกก่อน แล้วบังคับใช้ CA ของ certifi แทน
os.environ.pop("REQUESTS_CA_BUNDLE", None)
os.environ.pop("SSL_CERT_FILE", None)

from urllib.parse import urljoin, urlparse

import certifi
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}
TIMEOUT = 20


def fetch_html(url: str) -> str:
    """โหลด HTML ของ URL ด้วย requests (บังคับใช้ CA ของ certifi กันปัญหา SSL)"""
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT, verify=certifi.where())
    resp.raise_for_status()
    resp.encoding = resp.apparent_encoding or resp.encoding
    return resp.text


def looks_js_rendered(soup: BeautifulSoup) -> bool:
    """เดาคร่าว ๆ ว่าเว็บน่าจะ render ด้วย JS (ได้ HTML มาแทบไม่มีเนื้อหา)"""
    text = soup.get_text(strip=True)
    scripts = soup.find_all("script")
    return len(text) < 500 and len(scripts) >= 3


def parse_fields(fields_str: str):
    """
    แปลงสตริง fields เช่น  "title=.name, price=.price, link=a@href"
    เป็น list ของ {name, sel, attr}
    - name=selector           -> ดึง text
    - name=selector@attribute -> ดึงค่า attribute (เช่น a@href, img@src)
    """
    fields = []
    if not fields_str:
        return fields
    for part in fields_str.split(","):
        part = part.strip()
        if not part or "=" not in part:
            continue
        name, expr = part.split("=", 1)
        name, expr = name.strip(), expr.strip()
        attr = None
        if "@" in expr:
            expr, attr = expr.rsplit("@", 1)
            expr, attr = expr.strip(), attr.strip()
        fields.append({"name": name, "sel": expr, "attr": attr})
    return fields


def abs_url(base: str, value: str) -> str:
    return urljoin(base, value) if value else value


def extract_by_selector(soup, selector, fields, base_url):
    """โหมดเจาะจง: เลือก element ตาม CSS selector แล้วดึงข้อมูลออกมา"""
    items = []
    for el in soup.select(selector):
        if fields:
            row = {}
            for f in fields:
                target = el.select_one(f["sel"]) if f["sel"] else el
                if target is None:
                    row[f["name"]] = None
                elif f["attr"]:
                    val = target.get(f["attr"])
                    if f["attr"] in ("href", "src") and val:
                        val = abs_url(base_url, val)
                    row[f["name"]] = val
                else:
                    row[f["name"]] = target.get_text(" ", strip=True)
            items.append(row)
        else:
            row = {"text": el.get_text(" ", strip=True)}
            a = el.select_one("a[href]")
            if a:
                row["link"] = abs_url(base_url, a.get("href"))
            img = el.select_one("img[src]")
            if img:
                row["image"] = abs_url(base_url, img.get("src"))
            items.append(row)
    return {"items": items}


def extract_auto(soup, base_url):
    """โหมดอัตโนมัติ: ดึงข้อมูลชนิดที่พบบ่อยมาให้หลายชุด"""
    datasets = {}

    headings = []
    for tag in soup.select("h1, h2, h3"):
        txt = tag.get_text(" ", strip=True)
        if txt:
            headings.append({"level": tag.name, "text": txt})
    if headings:
        datasets["หัวข้อ (headings)"] = headings

    links = []
    seen = set()
    for a in soup.select("a[href]"):
        href = abs_url(base_url, a.get("href"))
        txt = a.get_text(" ", strip=True)
        if href and href not in seen and not href.startswith("javascript:"):
            seen.add(href)
            links.append({"text": txt, "url": href})
    if links:
        datasets["ลิงก์ (links)"] = links

    images = []
    for img in soup.select("img[src]"):
        images.append(
            {"image": abs_url(base_url, img.get("src")), "alt": img.get("alt", "")}
        )
    if images:
        datasets["รูปภาพ (images)"] = images

    tables = []
    for ti, table in enumerate(soup.select("table"), start=1):
        headers = [th.get_text(" ", strip=True) for th in table.select("tr th")]
        for tr in table.select("tr"):
            cells = tr.select("td")
            if not cells:
                continue
            values = [td.get_text(" ", strip=True) for td in cells]
            if headers and len(headers) == len(values):
                row = dict(zip(headers, values))
            else:
                row = {f"col{i+1}": v for i, v in enumerate(values)}
            row["_table"] = ti
            tables.append(row)
    if tables:
        datasets["ตาราง (tables)"] = tables

    paragraphs = []
    for p in soup.select("p"):
        txt = p.get_text(" ", strip=True)
        if len(txt) > 20:
            paragraphs.append({"text": txt})
    if paragraphs:
        datasets["ย่อหน้า (paragraphs)"] = paragraphs

    return datasets


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scrape", methods=["POST"])
def scrape():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    selector = (data.get("selector") or "").strip()
    fields_str = (data.get("fields") or "").strip()

    if not url:
        return jsonify({"ok": False, "error": "กรุณาใส่ URL"}), 400
    if not urlparse(url).scheme:
        url = "https://" + url  # เผื่อพิมพ์มาไม่มี http

    try:
        html = fetch_html(url)
    except requests.exceptions.SSLError:
        return jsonify({"ok": False, "error": "ต่อ SSL ไม่ได้ (ใบรับรองเว็บมีปัญหา)"}), 502
    except requests.exceptions.RequestException as e:
        return jsonify({"ok": False, "error": f"โหลดหน้าเว็บไม่สำเร็จ: {e}"}), 502

    soup = BeautifulSoup(html, "lxml")
    page_title = soup.title.get_text(strip=True) if soup.title else ""

    if selector:
        datasets = extract_by_selector(soup, selector, parse_fields(fields_str), url)
        mode = "selector"
    else:
        datasets = extract_auto(soup, url)
        mode = "auto"

    total = sum(len(rows) for rows in datasets.values())
    return jsonify(
        {
            "ok": True,
            "url": url,
            "title": page_title,
            "mode": mode,
            "js_rendered": looks_js_rendered(soup),
            "count": total,
            "datasets": datasets,
        }
    )


if __name__ == "__main__":
    print("เปิดเบราว์เซอร์ไปที่  http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
