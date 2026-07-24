"""
utils.py
ฟังก์ชันช่วยเหลือที่ scraper ทุกตัวใช้ร่วมกัน: ดึงหน้าเว็บ, หน่วงเวลา, เซฟไฟล์
"""

import csv
import json
import os
import time

import requests

import config


def fetch(url: str) -> requests.Response:
    """
    โหลดหน้าเว็บ 1 หน้า พร้อม header + timeout
    raise_for_status() จะ throw error ถ้าเจอ 404 / 500 จะได้รู้ตัวว่าดึงพลาด
    """
    resp = requests.get(url, headers=config.HEADERS, timeout=config.REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp


def polite_sleep():
    """หน่วงเวลาตามที่ตั้งใน config เพื่อไม่ยิง request ถี่เกินไป"""
    time.sleep(config.REQUEST_DELAY)


def save_json(data: list, filename: str):
    """เซฟ list ของ dict เป็นไฟล์ JSON"""
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    path = os.path.join(config.OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  บันทึก JSON -> {path} ({len(data)} รายการ)")


def save_csv(data: list, filename: str):
    """เซฟ list ของ dict เป็นไฟล์ CSV (คอลัมน์ยึดจาก key ของ dict ตัวแรก)"""
    if not data:
        print("  ไม่มีข้อมูลให้บันทึก")
        return
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    path = os.path.join(config.OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
    print(f"  บันทึก CSV  -> {path} ({len(data)} รายการ)")
