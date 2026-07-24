# Web Scraping Starter 🕷️

โปรเจกต์ตัวอย่างสำหรับฝึก web scraping ด้วย Python มี **2 วิธีใช้งาน**:

1. **CLI** (`run.py`) — สคริปต์สำเร็จรูปดึง 2 เว็บฝึกซ้อม เซฟลงไฟล์
2. **เว็บแอป** (`app.py`) — หน้าเว็บให้แปะ URL "ไหนก็ได้" แล้วดูข้อมูลเป็นตาราง + ดาวน์โหลด

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

### 3. รัน (เลือกแบบใดแบบหนึ่ง)

**แบบ CLI — ดึง 2 เว็บฝึกซ้อม เซฟลงไฟล์**

```bash
python run.py books      # ดึงเฉพาะหนังสือ
python run.py quotes     # ดึงเฉพาะคำคม
python run.py all        # ดึงทั้งสองอย่าง
python run.py            # ไม่ใส่อะไร = ดึงทั้งหมด
```

ผลลัพธ์จะถูกเซฟลงโฟลเดอร์ `output/` ทั้งแบบ `.json` และ `.csv`
(ไฟล์ CSV เปิดใน Excel แล้วภาษาไทยไม่เพี้ยน เพราะเซฟแบบ UTF-8 with BOM)

**แบบเว็บแอป — แปะ URL ไหนก็ได้ผ่านเบราว์เซอร์** (ดูรายละเอียดหัวข้อ [เว็บแอป](#เว็บแอป-แปะ-url-แล้วดูข้อมูล) ด้านล่าง)

```bash
python app.py
```

แล้วเปิดเบราว์เซอร์ไปที่ **http://127.0.0.1:5000**

### 4. ทดสอบ logic (ไม่ต้องต่อเน็ต)

```bash
python test_parsers.py
```

---

## เว็บแอป (แปะ URL แล้วดูข้อมูล)

รัน `python app.py` แล้วเปิด **http://127.0.0.1:5000** — แปะ URL ของเว็บอะไรก็ได้
แล้วกดดึงข้อมูลออกมาดูเป็นตาราง ดาวน์โหลดเป็น JSON / CSV ได้ทันที

**ทำไมต้องมี server:** เบราว์เซอร์ scrape เว็บอื่นตรง ๆ ไม่ได้ (ติด CORS)
`app.py` เลยเป็นตัวกลางไป fetch HTML ให้ แล้วส่งข้อมูลกลับมาโชว์บนหน้าเว็บ

**2 โหมดการใช้งาน:**

- **โหมดอัตโนมัติ** (ไม่ใส่ selector) — ดึง หัวข้อ / ลิงก์ / รูป / ตาราง / ย่อหน้า มาให้ แยกเป็นแท็บ
- **โหมดเจาะจง** (กด "ตัวเลือกขั้นสูง") — ระบุ CSS selector เลือกเฉพาะที่ต้องการ เช่น
  - Selector: `article.product_pod`
  - Fields: `title=h3 a@title, price=.price_color, link=h3 a@href`
  - ต่อท้ายด้วย `@attr` เพื่อดึง attribute (เช่น `a@href`, `img@src`) — ไม่ใส่ = ดึงข้อความ

> 💡 ไม่รู้ selector? เปิด DevTools (F12) คลิกขวาที่ element → Copy → Copy selector

**ข้อจำกัดที่ควรรู้:**

- เว็บ **JS-rendered** (React/Vue/SPA) จะดึงไม่ได้ครบ — แอปจะขึ้นแถบเตือนสีเหลืองให้
  (ต้องใช้ Playwright แทน ดูตัวอย่างใน `scrapers/quotes_js_scraper.py`)
- บางเว็บ block bot หรือต้อง login → อาจดึงไม่ได้

---

## โครงสร้างไฟล์

```
web-scraping-starter/
├── run.py                      # [CLI] ไฟล์หลัก สั่งรันจากตรงนี้
├── app.py                      # [เว็บแอป] Flask server แปะ URL ไหนก็ได้ผ่านเบราว์เซอร์
├── config.py                   # ค่า setting ทั้งหมด (URL, delay, จำนวนหน้า)
├── utils.py                    # ฟังก์ชันช่วยเหลือ (โหลดหน้า, เซฟไฟล์)
├── test_parsers.py             # เทส logic การ parse แบบ offline
├── requirements.txt
├── templates/
│   └── index.html              # หน้าเว็บ UI ของ app.py
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

## แก้ปัญหาที่เจอบ่อย

**รัน `run.py` แล้วเจอ `SSL: CERTIFICATE_VERIFY_FAILED`**

มักเกิดกับเครื่องที่ตั้ง environment variable `REQUESTS_CA_BUNDLE` / `SSL_CERT_FILE`
ค้างไว้ (เช่นเคยติดตั้ง mitmproxy) ทำให้ Python เชื่อเฉพาะ CA ตัวนั้น พอต่อเว็บตรง ๆ เลย verify ไม่ผ่าน
วิธีแก้ — เคลียร์ env สองตัวนี้ก่อนรัน:

```powershell
# PowerShell (เฉพาะ session นี้)
$env:REQUESTS_CA_BUNDLE=""; $env:SSL_CERT_FILE=""
python run.py all
```

(หมายเหตุ: `app.py` จัดการเรื่องนี้ให้อัตโนมัติอยู่แล้ว ไม่ต้องเคลียร์เอง)

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
