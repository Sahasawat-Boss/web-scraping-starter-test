"""
config.py
รวมค่า setting ทั้งหมดไว้ที่เดียว จะได้ไม่ต้องไปแก้กระจายในหลายไฟล์
"""

# เว็บเป้าหมาย (2 ตัวนี้ทำมาสำหรับฝึก scrape โดยเฉพาะ ปลอดภัย)
BOOKS_BASE_URL = "https://books.toscrape.com/"
QUOTES_BASE_URL = "https://quotes.toscrape.com/"

# หน่วงเวลาระหว่างแต่ละ request (วินาที) — มารยาทพื้นฐาน อย่ายิงถี่จนไปกวนเซิร์ฟเวอร์เขา
REQUEST_DELAY = 1.0

# ตั้ง timeout กันค้างเวลาเว็บไม่ตอบ
REQUEST_TIMEOUT = 15

# แกล้งทำตัวเป็น browser จริง เว็บบางที่จะ block ถ้าไม่มี User-Agent
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0 Safari/537.36"
    )
}

# scrape กี่หน้า (pagination) — ตั้งไว้ต่ำ ๆ ตอนเทส แล้วค่อยเพิ่ม
MAX_PAGES = 3

# โฟลเดอร์เก็บผลลัพธ์
OUTPUT_DIR = "output"
