# Web Scraping Starter 🕷️

โปรเจกต์ตัวอย่างสำหรับฝึก web scraping ด้วย Python
ดึงข้อมูลจากเว็บที่ทำมาสำหรับฝึกโดยเฉพาะ ปลอดภัย ถูกกฎหมาย ไม่ต้องกังวลเรื่องไปกวนเว็บใคร

- **books.toscrape.com** — ร้านหนังสือจำลอง (ดึง ชื่อ/ราคา/เรตติ้ง/สต็อก)
- **quotes.toscrape.com** — คำคม (ดึง ข้อความ/ผู้เขียน/แท็ก)

ทั้งสองเว็บสร้างโดยทีม Scrapy ตั้งใจให้คนมาฝึกโดยเฉพาะ

---

## เริ่มใช้งาน

### 1. เตรียม environment (แนะนำให้ใช้ virtual env)

```bash
python -m venv venv

# Windows
venv\Scripts\activate
# Mac / Linux
source venv/bin/activate
```

### 2. ติดตั้ง library

```bash
pip install -r requirements.txt
```

### 3. รัน

```bash
python run.py books      # ดึงเฉพาะหนังสือ
python run.py quotes     # ดึงเฉพาะคำคม
python run.py all        # ดึงทั้งสองอย่าง
python run.py            # ไม่ใส่อะไร = ดึงทั้งหมด
```

ผลลัพธ์จะถูกเซฟลงโฟลเดอร์ `output/` ทั้งแบบ `.json` และ `.csv`
(ไฟล์ CSV เปิดใน Excel แล้วภาษาไทยไม่เพี้ยน เพราะเซฟแบบ UTF-8 with BOM)

### 4. ทดสอบ logic (ไม่ต้องต่อเน็ต)

```bash
python test_parsers.py
```

---

## โครงสร้างไฟล์

```
web-scraping-starter/
├── run.py                      # ไฟล์หลัก สั่งรันจากตรงนี้
├── config.py                   # ค่า setting ทั้งหมด (URL, delay, จำนวนหน้า)
├── utils.py                    # ฟังก์ชันช่วยเหลือ (โหลดหน้า, เซฟไฟล์)
├── test_parsers.py             # เทส logic การ parse แบบ offline
├── requirements.txt
├── scrapers/
│   ├── books_scraper.py        # scrape หนังสือ (static + pagination)
│   ├── quotes_scraper.py       # scrape คำคม (static)
│   └── quotes_js_scraper.py    # ตัวอย่างเว็บ JS-rendered (optional)
└── output/                     # ผลลัพธ์เก็บที่นี่
```

---

## แนวคิดหลัก (อ่านแล้วต่อยอดเองได้)

การ scrape เว็บ static มี 3 สเต็ปเสมอ:

1. **โหลด HTML** — ยิง `requests.get(url)` ได้ HTML ทั้งหน้ามา
2. **แกะข้อมูล** — เอา `BeautifulSoup` มาเลือก element ด้วย CSS selector
   (เหมือน `document.querySelector` ในฝั่ง frontend เป๊ะ ๆ)
3. **เก็บข้อมูล** — เซฟลง JSON / CSV / database

สำหรับคนทำ frontend มาแล้ว จุดที่คุ้นที่สุดคือ selector เช่น
`soup.select_one("p.price_color")` ก็คือ `.price_color` ที่เราใช้อยู่ทุกวัน

### static vs JavaScript-rendered

- **static** — ข้อมูลอยู่ใน HTML ตั้งแต่ server ส่งมา → ใช้ `requests` พอ (เร็ว เบา)
- **JS-rendered** — ข้อมูลถูก JavaScript ยัดเข้ามาทีหลัง (React/Vue/SPA)
  → `requests` จะได้หน้าเปล่า ต้องใช้ browser จริงอย่าง **Playwright**
  (ดูตัวอย่างใน `scrapers/quotes_js_scraper.py`)

  วิธีเช็คเร็ว ๆ ว่าเว็บเป็นแบบไหน: กด View Source (Ctrl+U) แล้วค้นหาข้อมูลที่ต้องการ
  ถ้าเจอใน source = static / ถ้าไม่เจอ = JS-rendered

---

## ปรับแต่ง

แก้ที่ `config.py`:

- `MAX_PAGES` — จะดึงกี่หน้า (ตอนเทสตั้งน้อย ๆ ก่อน)
- `REQUEST_DELAY` — หน่วงเวลาระหว่าง request (วินาที) อย่าตั้ง 0 เพื่อความสุภาพ
- `HEADERS` — แก้ User-Agent ได้

---

## มารยาทในการ scrape (สำคัญ)

- เช็ค `robots.txt` ของเว็บก่อน (เช่น `https://เว็บ.com/robots.txt`)
- อ่าน Terms of Service — บางเว็บห้าม scrape
- อย่ายิง request ถี่เกินไป (ใส่ delay เสมอ)
- หลีกเลี่ยงการดึงข้อมูลส่วนบุคคล
- ถ้าเว็บมี API อย่างเป็นทางการ ใช้ API ดีกว่า scrape

---

## ต่อยอดจากตรงนี้

- ลองเปลี่ยน selector ให้ดึงข้อมูลเพิ่ม (เช่น เข้าไปหน้า detail ของหนังสือแต่ละเล่ม)
- เปลี่ยนเป้าหมายเป็นเว็บอื่น (เริ่มจากเว็บ static ง่าย ๆ ก่อน)
- เซฟลง database แทนไฟล์ (SQLite / PostgreSQL)
- ตั้ง schedule ให้รันอัตโนมัติ (cron / Task Scheduler)
