"""
quotes_js_scraper.py  (OPTIONAL — ต้องติดตั้ง Playwright เพิ่มก่อน)
--------------------------------------------------------------------
ตัวอย่างการ scrape เว็บที่ render ด้วย JavaScript

quotes.toscrape.com/js/ หน้าตาเหมือนเวอร์ชันปกติ แต่ข้อมูลถูกยัดเข้ามา
ด้วย JavaScript หลังหน้าโหลด ถ้าใช้ requests ธรรมดาจะได้ HTML เปล่า ๆ
เลยต้องเปิด browser จริง (headless) ให้มันรัน JS ก่อน แล้วค่อยอ่าน DOM

วิธีติดตั้ง (ทำครั้งเดียว):
    pip install playwright
    playwright install chromium

แล้วค่อยรัน:
    python -c "from scrapers.quotes_js_scraper import scrape; print(scrape()[:2])"
--------------------------------------------------------------------
"""

import config


def scrape() -> list:
    # import ไว้ในฟังก์ชัน เพื่อให้คนที่ยังไม่ลง Playwright ยังรันไฟล์อื่นได้ปกติ
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise SystemExit(
            "ยังไม่ได้ติดตั้ง Playwright\n"
            "รัน:  pip install playwright  แล้ว  playwright install chromium"
        )

    all_quotes = []
    url = config.QUOTES_BASE_URL + "js/"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # headless = ไม่เปิดหน้าต่างจริง
        page = browser.new_page()

        page_num = 1
        while page_num <= config.MAX_PAGES:
            print(f"[quotes-js] กำลังดึงหน้า {page_num} ...")
            page.goto(url if page_num == 1 else f"{config.QUOTES_BASE_URL}js/page/{page_num}/")
            page.wait_for_selector("div.quote")  # รอจน JS ยัดข้อมูลเสร็จ

            boxes = page.query_selector_all("div.quote")
            for box in boxes:
                all_quotes.append({
                    "quote": box.query_selector("span.text").inner_text(),
                    "author": box.query_selector("small.author").inner_text(),
                })

            # เช็คว่ามีปุ่ม next ไหม
            if not page.query_selector("li.next a"):
                break
            page_num += 1

        browser.close()

    print(f"[quotes-js] ดึงมาได้ทั้งหมด {len(all_quotes)} quote")
    return all_quotes
