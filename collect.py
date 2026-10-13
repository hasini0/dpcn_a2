#!/usr/bin/env python3
"""Step 1 - collect Group 23 data from OpenAlex  ->  raw/*.json

Group 23: S.N. Bose Centre, Bose Institute, SINP (Kolkata) + NCBS Bangalore.
Usage:  python collect.py you@email.com
Needs internet (api.openalex.org). Takes ~10-30 min. Resumable (cached in raw/).
"""
import json, os, sys, time, requests

MAILTO = sys.argv[1] if len(sys.argv) > 1 else "your@email.com"
API_KEY = (sys.argv[2] if len(sys.argv) > 2 else os.environ.get("OPENALEX_API_KEY", "")).strip()
API = "https://api.openalex.org"
RAW = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raw")
os.makedirs(RAW, exist_ok=True)

# (display name used in CSV, search string for OpenAlex institution lookup)
INSTITUTIONS = [
    ("SN Bose National Centre", "S.N. Bose National Centre for Basic Sciences"),
    ("Bose Institute Kolkata", "Bose Institute"),
    ("SINP Kolkata", "Saha Institute of Nuclear Physics"),
    ("NCBS Bangalore", "National Centre for Biological Sciences"),
]
# If a lookup picks the wrong entity, put the right OpenAlex ID here, e.g. "I1234567"
OVERRIDE_IDS = {}


class Refused(Exception):
    pass


class Quota(Exception):
    pass


def get(path, **params):
    params["mailto"] = MAILTO
    if API_KEY: params["api_key"] = API_KEY
    last = ""
    for attempt in range(8):
        try:
            r = requests.get(f"{API}/{path}", params=params, timeout=90)
        except requests.RequestException as e:
            last = f"network error: {e}"; time.sleep(5 * (attempt + 1)); continue
        if r.status_code == 429 or r.status_code >= 500:
            wait = float(r.headers.get("Retry-After", 0) or 0) or min(120, 5 * 2 ** attempt)
            last = f"HTTP {r.status_code}: {r.text[:300]}"
            if wait > 900:
                raise Quota(f"OpenAlex daily budget used up; it asks to wait {wait/3600:.1f} hours.")
            print(f"\n  [{r.status_code}] waiting {int(wait)}s then retrying ({attempt + 1}/8)...", flush=True)
            time.sleep(wait); continue
        if r.status_code >= 400:
            raise Refused(f"HTTP {r.status_code}: {r.text[:300]}")
        time.sleep(0.12)
        return r.json()
    raise Refused(last)


def cached(name, fn):
    p = os.path.join(RAW, name)
    if os.path.exists(p):
        return json.load(open(p))
    d = fn()
    json.dump(d, open(p, "w"))
    return d


def resolve():
    out = []
    for name, q in INSTITUTIONS:
        if name in OVERRIDE_IDS:
            out.append({"name": name, "id": OVERRIDE_IDS[name], "display": name}); continue
        res = get("institutions", search=q, filter="country_code:IN", per_page=5,
                  select="id,display_name,ror,works_count")["results"]
        print(f"\n[{name}] candidates for '{q}':")
        for r in res:
            print("   ", r["id"].split("/")[-1], r["display_name"], r["ror"], r["works_count"])
        if not res:
            sys.exit(f"No match for {q}. Set OVERRIDE_IDS.")
        out.append({"name": name, "id": res[0]["id"].split("/")[-1], "display": res[0]["display_name"]})
        print("    -> using", out[-1]["id"], out[-1]["display"])
    return out


def fetch_works(inst_ids):
    works, cursor = [], "*"
    sel = ("id,doi,title,publication_year,type,primary_location,cited_by_count,"
           "authorships,referenced_works,primary_topic")
    flt = (f"authorships.institutions.id:{'|'.join(inst_ids)},from_publication_date:2016-01-01,"
           "to_publication_date:2026-12-31,type:article|review|proceedings-article")
    while cursor:
        d = get("works", filter=flt, per_page=200, cursor=cursor, select=sel)
        works += d["results"]
        cursor = d["meta"].get("next_cursor")
        print(f"  works: {len(works)}/{d['meta']['count']}", end="\r")
    print()
    return works


def batched(ids, n=50):
    ids = list(ids)
    for i in range(0, len(ids), n):
        yield ids[i:i + n]


def fetch_authors(aids):
    out = {}
    for b in batched(aids):
        d = get("authors", filter="openalex:" + "|".join(b), per_page=50,
                select="id,display_name,summary_stats,works_count,cited_by_count")
        for a in d["results"]:
            out[a["id"].split("/")[-1]] = {
                "name": a["display_name"], "h": (a.get("summary_stats") or {}).get("h_index"),
                "works": a.get("works_count"), "cites": a.get("cited_by_count")}
    return out


def _light(w):
    return {"doi": w.get("doi"), "year": w.get("publication_year"),
            "insts": sorted({(i.get("display_name"), i.get("country_code"))
                             for a in (w.get("authorships") or []) for i in (a.get("institutions") or [])
                             if i.get("display_name")}, key=lambda t: (t[0], t[1] or ""))}


def resumable(name, batches, do_batch):
    """Run do_batch(b) over batches, saving progress so a re-run continues. Aborts after 5 straight failures."""
    p = os.path.join(RAW, name + ".partial.json")
    st = json.load(open(p)) if os.path.exists(p) else {"done": 0, "data": {}}
    fails = 0; t0 = time.time(); start = st["done"]
    for n in range(st["done"], len(batches)):
        try:
            st["data"].update(do_batch(batches[n])); fails = 0
        except Quota as e:
            json.dump(st, open(p, "w"))
            sys.exit(f"\nSTOPPED: {e}\nProgress is saved. Get a free API key (openalex.org/settings/api) and run:\n  python3 run_all.py YOUR_EMAIL YOUR_API_KEY")
        except Refused as e:
            fails += 1; print(f"\n  batch {n} skipped: {e}")
            if fails >= 5:
                json.dump(st, open(p, "w")); sys.exit(f"\nStopping: OpenAlex keeps refusing ({e}). Progress saved; wait a few minutes and re-run the same command.")
        st["done"] = n + 1
        left = len(batches) - st["done"]; el = time.time() - t0; per = el / max(1, st["done"] - start)
        print(f"  {name}: batch {st['done']}/{len(batches)}  ~{per:.0f}s each, about {left * per / 60:.0f} min left   ", end="\r", flush=True)
        if n % 5 == 0:
            json.dump(st, open(p, "w"))
    print()
    if os.path.exists(p): os.remove(p)
    return st["data"]


def fetch_light(wids):
    """Metadata (doi, year, institutions) of referenced works."""
    def one(b):
        d = get("works", filter="openalex:" + "|".join(b), per_page=100, select="id,doi,publication_year,authorships")
        return {w["id"].split("/")[-1]: _light(w) for w in d["results"]}
    return resumable("refs", list(batched(wids, 100)), one)


def fetch_citers(wids):
    """Works that cite our papers: doi, year, institutions, referenced_works."""
    def one(b):
        out, cursor = {}, "*"
        while cursor:
            d = get("works", filter="cites:" + "|".join(b), per_page=200, cursor=cursor,
                    select="id,doi,publication_year,authorships,referenced_works")
            for w in d["results"]:
                x = _light(w); x["refs"] = [r.split("/")[-1] for r in (w.get("referenced_works") or [])]
                out[w["id"].split("/")[-1]] = x
            cursor = d["meta"].get("next_cursor")
        return out
    return resumable("citers", list(batched(wids, 40)), one)


def fetch_full_authors(works, mine):
    """OpenAlex bulk results cut every author list at 100. For works with 100+ authors (CMS/ALICE-type) fetch the
    full list (free single-record calls) and keep only: author count, authorships from OUR institutions, all institutions."""
    todo = [w["id"].split("/")[-1] for w in works if len(w.get("authorships") or []) >= 100]
    print(f"  {len(todo)} papers have 100+ authors; fetching their complete author lists...")
    def one(b):
        wid = b[0]
        w = get(f"works/{wid}", select="id,authorships")
        auths = w.get("authorships") or []
        ours = [a for a in auths if any(
            ((i.get("id") or "").split("/")[-1] in mine) or any(l.split("/")[-1] in mine for l in (i.get("lineage") or []))
            for i in (a.get("institutions") or []))]
        insts = sorted({(i.get("display_name"), i.get("country_code")) for a in auths for i in (a.get("institutions") or []) if i.get("display_name")},
                       key=lambda t: (t[0], t[1] or ""))
        return {wid: {"n": len(auths), "mine": ours, "insts": insts}}
    return resumable("fullauth", [[t] for t in todo], one)


if __name__ == "__main__":
    insts = cached("institutions.json", resolve)
    ids = [i["id"] for i in insts]
    works = cached("works.json", lambda: fetch_works(ids))
    print(len(works), "works")
    mine = set(ids)
    full = cached("fullauth.json", lambda: fetch_full_authors(works, mine))
    def is_mine(a):
        return any(((i.get("id") or "").split("/")[-1] in mine) or any(l.split("/")[-1] in mine for l in (i.get("lineage") or []))
                   for i in (a.get("institutions") or []))
    aid_of = lambda a: (((a.get("author") or {}).get("id")) or "").split("/")[-1]
    aids = {aid_of(a) for w in works for a in (w.get("authorships") or []) if is_mine(a)}
    aids |= {aid_of(a) for r in full.values() for a in r["mine"]}
    aids.discard("")
    authors = cached("authors.json", lambda: {})
    missing = [a for a in aids if a not in authors]
    if missing:
        print(f"  fetching h-index for {len(missing)} authors...")
        authors.update(fetch_authors(missing)); json.dump(authors, open(os.path.join(RAW, "authors.json"), "w"))
    wid = [w["id"].split("/")[-1] for w in works]
    own = set(wid)
    refs = {r.split("/")[-1] for w in works for r in (w.get("referenced_works") or [])} - own
    cached("refs.json", lambda: fetch_light(refs))
    cached("citers.json", lambda: fetch_citers(wid))
    print("Done. Now run: python build.py")
