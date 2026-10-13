#!/usr/bin/env python3
"""Downloads Scimago journal rankings (for Q1-Q4 quartiles) and saves scimago.csv next to this file.
Run:  python3 fetch_scimago.py      then:  python3 build.py && python3 dashboard.py && python3 report.py
If it fails, download manually: scimagojr.com -> Journal Rankings -> 'Download data' -> save as scimago.csv here."""
import os, requests
HERE = os.path.dirname(os.path.abspath(__file__))
H = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/124 Safari/537.36"}
for year in (2025, 2024, 2023):
    url = f"https://www.scimagojr.com/journalrank.php?year={year}&type=j&out=xls"
    try:
        r = requests.get(url, headers=H, timeout=120)
        head = r.text[:400]
        if r.status_code == 200 and "Issn" in head and "Quartile" in head:
            open(os.path.join(HERE, "scimago.csv"), "w", encoding="utf-8").write(r.text)
            print(f"Saved scimago.csv (year {year}, {len(r.text.splitlines())} journals)."); break
        print(year, "-> not usable (HTTP", r.status_code, ")")
    except Exception as e:
        print(year, "-> failed:", e)
else:
    print("Could not download automatically. Please download it manually (see top of this file).")
