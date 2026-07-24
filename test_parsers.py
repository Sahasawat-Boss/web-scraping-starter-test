"""
test_parsers.py
ทดสอบ logic การ parse โดยไม่ต้องต่อเน็ต — ใช้ HTML ตัวอย่างที่หน้าตา
เหมือนของจริง ช่วยยืนยันว่าฟังก์ชัน parse ทำงานถูกก่อนเอาไปยิงเว็บจริง

รัน:  python test_parsers.py
"""

from bs4 import BeautifulSoup

from scrapers.books_scraper import parse_book
from scrapers.quotes_scraper import parse_quote

# HTML ตัวอย่าง โครงสร้างเหมือน books.toscrape.com
BOOK_HTML = """
<article class="product_pod">
  <p class="star-rating Three"></p>
  <h3><a href="../../a-book_1/index.html" title="A Great Book Title">A Great...</a></h3>
  <div class="product_price">
    <p class="price_color">£51.77</p>
    <p class="instock availability">In stock</p>
  </div>
</article>
"""

QUOTE_HTML = """
<div class="quote">
  <span class="text">"The world is what we think it is."</span>
  <small class="author">Jane Doe</small>
  <a class="tag">life</a>
  <a class="tag">wisdom</a>
</div>
"""


def test_book():
    soup = BeautifulSoup(BOOK_HTML, "lxml")
    article = soup.select_one("article.product_pod")
    result = parse_book(article, "https://books.toscrape.com/catalogue/page-1.html")

    assert result["title"] == "A Great Book Title", result["title"]
    assert result["price_gbp"] == 51.77, result["price_gbp"]
    assert result["rating"] == 3, result["rating"]
    assert result["availability"] == "In stock", result["availability"]
    assert result["url"].startswith("https://"), result["url"]
    print("PASS  parse_book ->", result)


def test_quote():
    soup = BeautifulSoup(QUOTE_HTML, "lxml")
    box = soup.select_one("div.quote")
    result = parse_quote(box)

    assert result["author"] == "Jane Doe", result["author"]
    assert "life" in result["tags"], result["tags"]
    assert "wisdom" in result["tags"], result["tags"]
    print("PASS  parse_quote ->", result)


if __name__ == "__main__":
    test_book()
    test_quote()
    print("\nผ่านหมดทุกเทส logic การ parse ถูกต้อง")
