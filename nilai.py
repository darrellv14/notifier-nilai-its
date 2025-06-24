import os
import time
import json
import schedule
import requests
from datetime import datetime
from bs4 import BeautifulSoup

URL = "https://akademik.its.ac.id/data_nilaimhs.php"
STATE_FILE = "state_sem6.json"

def load_cookies():
    jar = requests.cookies.RequestsCookieJar()
    cookie_str = os.getenv("COOKIE_NILAI", "")
    for pair in cookie_str.split(";"):
        if "=" in pair:
            name, val = pair.strip().split("=", 1)
            jar.set(name, val, domain="akademik.its.ac.id", path="/")
    return jar

def scrape():
    try:
        r = requests.get(URL, cookies=load_cookies(), timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"Error fetching page: {e}")
        return {}

    soup = BeautifulSoup(r.text, "html.parser")
    marker = soup.find(
        lambda tag: tag.name == "td" and "2024/GENAP" in tag.get_text(strip=True)
    )
    if not marker:
        print("⚠️ Tabel semester 6 tidak ditemukan")
        return {}

    table = marker.find_parent("table")
    data = {}
    for row in table.find_all("tr", valign="top"):
        cols = row.find_all("td")
        if len(cols) < 3:
            continue
        mk = cols[0].get_text(strip=True)
        nilai = cols[2].get_text(strip=True)
        data[mk] = nilai
    return data

def send_notify(msg):
    webhook = os.getenv("DISCORD_WEBHOOK", "")
    if not webhook:
        print("⚠️ DISCORD_WEBHOOK tidak diset")
        return
    try:
        resp = requests.post(webhook, json={"content": msg}, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"Error sending Discord notification: {e}")

def compare_and_notify():
    new = scrape()
    if not new:
        return

    old = {}
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                old = json.load(f)
        except Exception as e:
            print(f"Error reading state file: {e}")

    changed = {
        mk: n for mk, n in new.items()
        if mk in old and old[mk] in ("_", "-") and n not in ("_", "-")
    }

    if changed:
        msg = "**📢 Update Nilai Semester 6!**\n"
        for mk, n in changed.items():
            msg += f"- {mk}: **{n}**\n"
        msg += f"\n_Waktu: {datetime.now():%d %b %Y %H:%M}_"
        send_notify(msg)

    try:
        with open(STATE_FILE, "w") as f:
            json.dump(new, f, indent=2)
    except Exception as e:
        print(f"Error writing state file: {e}")

def main():
    schedule.every(15).minutes.do(compare_and_notify)
    compare_and_notify()
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
