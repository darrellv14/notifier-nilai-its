import os, time, json, schedule, requests
from datetime import datetime
from bs4 import BeautifulSoup

URL = "https://akademik.its.ac.id/data_nilaimhs.php"
STATE_FILE = "state_sem6.json"

def load_cookies():
    jar = requests.cookies.RequestsCookieJar()
    for pair in os.getenv("COOKIE_NILAI","").split(";"):
        if "=" in pair:
            name, val = pair.strip().split("=",1)
            jar.set(name, val, domain="akademik.its.ac.id", path="/")
    return jar

def scrape():
    r = requests.get(URL, cookies=load_cookies(), timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    # temukan header semester 6
    marker = soup.find(
        lambda tag: tag.name=="td" and "2024/GENAP" in tag.get_text(strip=True)
    )
    if not marker:
        print("⚠️ Tabel semester 6 tidak ditemukan")
        return {}
    table = marker.find_parent("table")
    data = {}
    for row in table.find_all("tr", valign="top"):
        cols = row.find_all("td")
        if len(cols) < 3: continue
        mk    = cols[0].get_text(strip=True)
        kelas = cols[1].get_text(strip=True)
        nilai = cols[2].get_text(strip=True)
        data[mk] = {"kelas": kelas, "nilai": nilai}
    return data

def send_notify(msg):
    webhook = os.getenv("DISCORD_WEBHOOK","")
    if not webhook: return
    requests.post(webhook, json={"content":msg}, timeout=10)

def compare_and_notify():
    new = scrape()
    if not new: return

    # old hanya simpan nilai string
    old = json.load(open(STATE_FILE)) if os.path.exists(STATE_FILE) else {}

    # deteksi perubahan: dulu "_" → sekarang bukan "_" / "-"
    changed = {
      mk: info for mk,info in new.items()
      if mk in old 
         and old[mk] in ("_","-") 
         and info["nilai"] not in ("_","-")
    }

    if changed:
        msg = "**📢 Update Nilai Semester 6!**\n"
        for mk, info in changed.items():
            msg += f"- {mk} | Kelas: `{info['kelas']}` | Nilai: **{info['nilai']}**\n"
        msg += f"\n_Waktu: {datetime.now():%d %b %Y %H:%M}_"
        send_notify(msg)

    # update state (hanya nilai)
    with open(STATE_FILE,"w") as f:
        json.dump({mk:info["nilai"] for mk,info in new.items()}, f, indent=2)

def main():
    schedule.every(15).minutes.do(compare_and_notify)
    compare_and_notify()
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__=="__main__":
    main()
