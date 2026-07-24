"""
run.py — ไฟล์หลักสำหรับสั่งรัน scraper
--------------------------------------------------------------------
วิธีใช้:
    python run.py books      # ดึงข้อมูลหนังสือ
    python run.py quotes     # ดึงคำคม
    python run.py all        # ดึงทั้งสองอย่าง (ค่า default ถ้าไม่ใส่อะไร)
--------------------------------------------------------------------
"""

import sys

from scrapers import books_scraper, quotes_scraper
from utils import save_csv, save_json


def run_books():
    print("\n=== เริ่ม scrape หนังสือ ===")
    data = books_scraper.scrape()
    save_json(data, "books.json")
    save_csv(data, "books.csv")


def run_quotes():
    print("\n=== เริ่ม scrape คำคม ===")
    data = quotes_scraper.scrape()
    save_json(data, "quotes.json")
    save_csv(data, "quotes.csv")


def main():
    # อ่าน argument ตัวแรก ถ้าไม่มีให้ default เป็น "all"
    target = sys.argv[1].lower() if len(sys.argv) > 1 else "all"

    if target == "books":
        run_books()
    elif target == "quotes":
        run_quotes()
    elif target == "all":
        run_books()
        run_quotes()
    else:
        print(f"ไม่รู้จักคำสั่ง '{target}'")
        print("ใช้ได้:  python run.py [books|quotes|all]")
        sys.exit(1)

    print("\nเสร็จแล้ว! ไปดูผลลัพธ์ที่โฟลเดอร์ output/")


if __name__ == "__main__":
    main()
