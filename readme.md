# Notifier Nilai ITS (Discord)

Sebuah _tool_ untuk memantau **nilai semester 6** pada SIAKAD ITS dan mengirim notifikasi ke **Discord** ketika nilai baru tersedia. Dirancang untuk dijalankan sebagai _scheduled job_ di **GitHub Actions** (self‑hosted runner) atau server lokal 24/7.

---

## Fitur

- Memantau perubahan nilai semester Genap 2024/2025 (semester 6)
- Mendukung notifikasi via **Discord Webhook**
- State file (`state_sem6.json`) untuk melacak nilai lama
- Dapat dijalankan otomatis dengan GitHub Actions (self-hosted) atau cron di server lokal

## Prasyarat

- Python 3.8 atau lebih baru
- Akses ke GitHub Self‑Hosted Runner atau server Linux/Windows yang selalu menyala
- **Discord Webhook URL** (simpan di secret `DISCORD_WEBHOOK`)
- **Cookie sesi** SIAKAD ITS (export `PHPSESSID=...`) disimpan di file `cookie.txt` atau secret `COOKIE_NILAI`

## Struktur Repo

```text
notifier-nilai-its/
├── nilai.py            # Skrip utama: scrape + notifikasi
├── run_once.py         # Pemicu run-once (compare_and_notify())
├── state_sem6.json     # State awal (semua nilai "_" untuk semester 6)
├── requirements.txt    # Daftar dependensi Python
└── .github/workflows/
    └── notifier.yml    # GitHub Actions workflow
```

## Instalasi & Konfigurasi

1. **Clone repository**:
   ```bash
   git clone https://github.com/USERNAME/notifier-nilai-its.git
   cd notifier-nilai-its
   ```

2. **Install dependensi**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. **Siapkan cookie SIAKAD**:
   - Export session cookie (`PHPSESSID=...`) dari browser setelah login dengan MFA.
   - Simpan di file `cookie.txt` di root repo:
     ```text
     PHPSESSID=MASUKKANCOOKIEANDADISINI
     ```

4. **Buat GitHub Self‑Hosted Runner**:
   - Di GitHub: **Settings → Actions → Runners → Add runner**
   - Ikuti instruksi instalasi di server Anda, pastikan label runner `self-hosted`
   - Runner ini akan memiliki folder workspace persisten untuk `cookie.txt` dan `state_sem6.json`

5. **Konfigurasi Secrets (jika masih pakai env var)**:
   - `DISCORD_WEBHOOK`: URL Webhook Discord
   - `COOKIE_NILAI`: (opsional) string cookie lengkap jika tidak pakai `cookie.txt`

## Workflow GitHub Actions

File: `.github/workflows/notifier.yml`

```yaml
name: Notifier Nilai ITS (Discord)

on:
  schedule:
    - cron: '*/15 * * * *'    # setiap 15 menit
  workflow_dispatch:          # manual trigger

jobs:
  notify:
    runs-on: [self-hosted, linux]
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run notifier once
        env:
          DISCORD_WEBHOOK: ${{ secrets.DISCORD_WEBHOOK }}
        run: python run_once.py
```

> **Catatan**: Runner self-hosted memiliki folder kerja yang **persisten**, sehingga `cookie.txt` dan `state_sem6.json` akan tetap tersedia di setiap run.

## Testing Lokal

1. Jalankan manual untuk verifikasi:
   ```bash
   python run_once.py
   ```
2. Pastikan pesan terkirim ke Discord sesuai nilai yang baru berubah.

## Troubleshooting

- **Tidak ada notifikasi** → periksa isi `state_sem6.json`, `cookie.txt`, dan akses page GET di `nilai.py`
- **Error import** → pastikan `pip install -r requirements.txt`
- **Discord webhook error** → cek URL Webhook di secret

## Lisensi

MIT © `2025` Darrell Valentino

