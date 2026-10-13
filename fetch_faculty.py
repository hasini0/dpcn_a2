#!/usr/bin/env python3
"""Official faculty rosters of the 4 Group-23 institutes  ->  faculty_roster.csv

OpenAlex has no "faculty" flag, so "authors with >= 5 papers" mixes faculty with students, postdocs,
visitors and outside collaborators. This script scrapes each institute's own People pages so build.py
can label every author as Faculty / Adjunct / Visiting / Former faculty / Not on any official list.

Usage:  python fetch_faculty.py          (pages are cached in raw/faculty_pages/)
"""
import csv, html, os, re, requests

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "raw", "faculty_pages")
os.makedirs(CACHE, exist_ok=True)

# (institution, category, url, parser)
PAGES = [
    ("NCBS Bangalore", "Faculty", "https://www.ncbs.res.in/faculty", "ncbs"),
    ("NCBS Bangalore", "Adjunct faculty", "https://www.ncbs.res.in/adjunct-faculty", "ncbs"),
    ("NCBS Bangalore", "Visiting faculty", "https://www.ncbs.res.in/visiting-faculty", "ncbs"),
    ("NCBS Bangalore", "Faculty associate (TIFR)", "https://www.ncbs.res.in/faculty-associates", "ncbs"),
    ("NCBS Bangalore", "Former faculty", "https://www.ncbs.res.in/former-faculty", "ncbs"),
    ("SN Bose National Centre", "Faculty", "https://newweb.bose.res.in/people/faculty", "snb"),
    ("Bose Institute Kolkata", "Faculty", "https://jcbose.ac.in/faculty", "jcb"),
    ("Bose Institute Kolkata", "Research scientist", "https://jcbose.ac.in/research-scientist", "jcb"),
    ("Bose Institute Kolkata", "Former faculty", "https://jcbose.ac.in/former-faculty", "jcb"),
] + [("SINP Kolkata", "Faculty", f"https://www.saha.ac.in/web/scientific?page={i}", "sinp") for i in range(1, 5)] \
  + [("SINP Kolkata", "Visiting scientist / research associate",
      f"https://www.saha.ac.in/web/visiting-scientists-research-associates?page={i}", "sinp") for i in range(1, 3)]


def fetch(url):
    p = os.path.join(CACHE, re.sub(r"[^A-Za-z0-9]+", "_", url.split("//", 1)[1]) + ".html")
    if not os.path.exists(p):
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
        if len(r.text) < 5000: r.raise_for_status()   # saha.ac.in answers 500 but still serves the full page
        open(p, "w", encoding="utf-8").write(r.text)
    return open(p, encoding="utf-8", errors="ignore").read()


strip = lambda s: re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s))).strip()
TITLE = re.compile(r"^(prof\.?|dr\.?|professor)\s*", re.I)


def parse_ncbs(t):
    for m in re.finditer(r"<strong><a href='[^']*'[^>]*>(.*?)</a></strong>(.*?)</div>", t, re.S):
        name = TITLE.sub("", strip(m.group(1))).split(",")[0]
        yield name, strip(m.group(2))[:120]
    for m in re.finditer(r"<a [^>]*>\s*((?:Prof|Dr)\.[^<]{3,60}?)\s*</a>(.*?)</div>", t, re.S):   # faculty-associates layout
        yield TITLE.sub("", strip(m.group(1))), strip(m.group(2))[:120]


def parse_snb(t):
    # several tables, each preceded by <h3 class="caption">Scheme</h3> (Faculty, CSIR Emeritus, ...)
    caption = "Faculty"
    for m in re.finditer(r"<h3 class=\"caption\">(.*?)</h3>|<tr class='(?:even|odd)'>(.*?)</tr>", t, re.S):
        if m.group(1):
            caption = strip(m.group(1)); caption = "Faculty" if caption == "SNBNCBS" else caption; continue
        cells = re.findall(r"<td>(.*?)</td>", m.group(2), re.S)
        if len(cells) >= 3:
            yield strip(cells[1]), (strip(cells[2]) + ("" if caption == "Faculty" else f" ({caption})"))[:120]


def parse_jcb(t):
    for m in re.finditer(r"<td><a href=\"https://jcbose.ac.in/(?:faculty|research-scientist)-details/[^\"]*\">(.*?)</a></td>\s*(?:<!--td[^>]*>(.*?)</td-->)?\s*<td[^>]*>(.*?)</td>", t, re.S):
        yield strip(m.group(1)), strip(m.group(2) or m.group(3))


def parse_sinp(t):
    for m in re.finditer(r"personal-page\?mid=[^\"]*\">(.*?)</a>(.*?)</tr>", t, re.S):
        rest = [strip(c) for c in re.findall(r"<td[^>]*>(.*?)</td>", m.group(2), re.S)]
        desig = next((c for c in rest if re.search(r"prof|scientist|director|associate|fellow|engineer", c, re.I)), "")
        yield strip(m.group(1)), desig


def main():
    rows, seen = [], set()
    for inst, cat, url, kind in PAGES:
        try:
            t = fetch(url)
        except Exception as e:
            print("  !! could not fetch", url, e); continue
        n = 0
        for name, desig in globals()["parse_" + kind](t):
            name = re.sub(r"\s+", " ", name).strip()
            if not name or (inst, cat, name.lower()) in seen: continue
            seen.add((inst, cat, name.lower())); n += 1
            c = cat
            if re.search(r"emeritus", desig, re.I): c = "Emeritus"
            if re.search(r"adjunct", desig, re.I) and cat == "Faculty" and not re.search(r"professor|scientist", desig.split("Adjunct")[0], re.I): c = "Adjunct faculty"
            if kind == "jcb" and cat == "Former faculty": c = "Former faculty"
            rows.append({"institution": inst, "name": name, "category": c, "designation": desig, "source": url})
        print(f"  {inst:25s} {cat:40s} {n:3d}  {url}")
    with open(os.path.join(HERE, "faculty_roster.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["institution", "name", "category", "designation", "source"])
        w.writeheader(); w.writerows(rows)
    print(len(rows), "roster entries -> faculty_roster.csv")


if __name__ == "__main__":
    main()
