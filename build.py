#!/usr/bin/env python3
"""Step 2 - turn raw/ into the submission files + metrics.

Outputs (in out/):
  group23_data.csv, citation_network.csv, authorship_network.csv, indian_connections.csv
  metrics.json  (feeds the dashboard and report)
Optional: put Scimago's journal CSV (scimagojr.com -> Download data) at scimago.csv
to fill journal quartiles. Without it quartile is blank (OpenAlex has no quartiles).
"""
import csv, json, os, itertools, collections as C
import pandas as pd, networkx as nx

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.environ.get("RAW_DIR") or os.path.join(HERE, "raw")
OUT = os.environ.get("OUT_DIR") or os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
GROUP = 23
FACULTY_MIN_PAPERS = 5  # an author needs >= this many papers in the corpus to count as "faculty" (OpenAlex has no faculty flag)
import re
_CANON = {}
def clean_journal(n):
    if not n: return ""
    parts = n.split("/")
    norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
    if len(parts) == 2 and norm(parts[0]) == norm(parts[1]): n = parts[0]
    n = re.sub(r"\.\s+(?=[A-Za-z]\b)", " ", n).strip().rstrip(".")
    n = n.replace("Physical review", "Physical Review")
    return _CANON.setdefault(norm(n), n)
MAX_AUTH = 100          # papers with more authors (CMS/ALICE-type) are skipped for co-author pairs
L = lambda f: json.load(open(os.path.join(RAW, f)))
insts, works, authors, refs, citers = (L("institutions.json"), L("works.json"), L("authors.json"),
                                       L("refs.json"), L("citers.json"))
FULL = L("fullauth.json") if os.path.exists(os.path.join(RAW, "fullauth.json")) else {}   # complete author lists for 100+ author papers
short = lambda x: x.split("/")[-1] if x else x
ID2NAME = {i["id"]: i["name"] for i in insts}          # assigned institutions
ID2DISP = {i["id"]: i["display"] for i in insts}
NAMES = [i["name"] for i in insts]
ASSIGNED_DISPLAY = set(ID2DISP.values())

# ---- Scimago quartiles ----
Q = {}
sp = os.path.join(HERE, "scimago.csv")
if os.path.exists(sp):
    s = pd.read_csv(sp, sep=";", dtype=str)
    qc = [c for c in s.columns if "Quartile" in c][0]
    for iss, q in zip(s["Issn"].fillna(""), s[qc]):
        for x in iss.replace(" ", "").split(","):
            if x and isinstance(q, str): Q[x] = q
def quartile(src):
    if not src: return ""
    for x in [src.get("issn_l")] + (src.get("issn") or []):
        if x and x.replace("-", "") in Q: return Q[x.replace("-", "")]
    return ""

own = {short(w["id"]) for w in works}
OWN_DISP = {n: set() for n in NAMES}          # display names that belong to each assigned institution (incl. child units)
for i in insts: OWN_DISP[i["name"]].add(i["display"])
def match_mine(inst_objs):
    out = []
    for i in inst_objs:
        ids = {short(i.get("id"))} | {short(l) for l in (i.get("lineage") or [])}
        for x in ids:
            if x in ID2NAME:
                if ID2NAME[x] not in out: out.append(ID2NAME[x])
                if i.get("display_name"): OWN_DISP[ID2NAME[x]].add(i["display_name"])
    return out
def insts_of(w):   # list of (display, country) for any light record
    return w["insts"]

# ---- per-work parsed record ----
P = {}
for w in works:
    wid = short(w["id"]); src = (w.get("primary_location") or {}).get("source") or {}
    is_conf = src.get("type") == "conference" or w["type"] == "proceedings-article"
    auths, allinst = [], set()
    fa = FULL.get(wid); n_auth = len(w["authorships"])
    shipments = list(w["authorships"])
    if fa:
        have = {(x.get("author") or {}).get("id") for x in shipments}
        shipments += [x for x in fa["mine"] if (x.get("author") or {}).get("id") not in have]
        n_auth = max(n_auth, fa["n"]); allinst |= {tuple(t) for t in fa["insts"]}
    for a in shipments:
        mine = match_mine(a["institutions"])
        others = [(i["display_name"], i.get("country_code")) for i in a["institutions"] if i.get("display_name")]
        allinst |= set(others)
        au = a.get("author") or {}
        nm = au.get("display_name") or "Unknown"
        auths.append({"id": short(au.get("id")) or "name:" + nm, "name": nm,
                      "mine": mine, "insts": others})
    topic = w.get("primary_topic") or {}
    P[wid] = {"id": wid, "doi": w.get("doi") or "", "title": w["title"] or "", "year": w["publication_year"],
              "type": "conference" if is_conf else "journal", "journal": clean_journal(src.get("display_name")),
              "issn": src.get("issn_l") or "", "quartile": "" if is_conf else quartile(src),
              "cites": w.get("cited_by_count") or 0, "n_auth": n_auth, "auths": auths, "allinst": allinst, "refs": [short(r) for r in (w.get("referenced_works") or [])],
              "field": (topic.get("field") or {}).get("display_name") or "Unknown",
              "subfield": (topic.get("subfield") or {}).get("display_name") or "Unknown",
              "inst": sorted({m for a in auths for m in a["mine"]}, key=NAMES.index)}

unattributed = [p for p in P.values() if not p["inst"]]
print(f"papers fetched: {len(P)}; attributed to an assigned institution: {len(P) - len(unattributed)}; NOT attributable: {len(unattributed)}")
if unattributed:
    top = C.Counter(n for p in unattributed for n, c in p["allinst"]).most_common(8)
    print("  institutions on the non-attributable papers:", top)
    for p in unattributed: p["year"] = 0      # excluded everywhere (dataset, stats, networks)
def indian_others(insts_list, exclude_display):
    return sorted({n for n, c in insts_list if c == "IN" and n not in exclude_display})

# citers per own paper
citers_of = C.defaultdict(list)
for cid, c in citers.items():
    for r in c["refs"]:
        if r in own: citers_of[r].append(cid)

# ---- main dataset ----
rows = []
for p in P.values():
    for name in p["inst"]:
        excl = set(OWN_DISP[name])
        coinst = indian_others(p["allinst"], excl)
        ref_in = set()
        for r in p["refs"]:
            ins = P[r]["allinst"] if r in P else (refs[r]["insts"] if r in refs else [])
            ref_in |= set(indian_others(ins, excl))
        cited_in = any(indian_others(citers[c]["insts"], excl) for c in citers_of[p["id"]])
        seen_ids = set()
        seen_names = set()
        for a in p["auths"]:
            nm_key = a["name"].strip().lower()
            if name in a["mine"] and a["id"] not in seen_ids and nm_key not in seen_names:
                seen_ids.add(a["id"])
                seen_names.add(nm_key)
                rows.append({"group": GROUP, "institution": name, "author": a["name"], "title": p["title"],
                             "year": p["year"], "type": p["type"], "journal_name": p["journal"], "issn": p["issn"],
                             "doi": p["doi"], "citations": p["cites"], "quartile": p["quartile"],
                             "coauthor_institutes": ";".join(coinst), "cites_indian_inst": bool(ref_in),
                             "cited_by_indian_inst": bool(cited_in)})
df = pd.DataFrame(rows)
df = df[(df.year >= 2016) & (df.year <= 2026)]
df.to_csv(f"{OUT}/group{GROUP}_data.csv", index=False)

# ---- citation network (file) ----
def inst_label(insts_list, mine=None):
    if mine: return mine[0]
    ind = [n for n, c in insts_list if c == "IN"]
    if ind: return ind[0]
    return insts_list[0][0] if insts_list else "Unknown"
edges, seen = [], set()
def add(sd, td, si, ti, y):
    if sd and td and (sd, td) not in seen:
        seen.add((sd, td)); edges.append({"source_doi": sd, "target_doi": td, "source_inst": si, "target_inst": ti, "year": y})
for p in P.values():
    if not p["inst"]: continue
    for r in p["refs"]:
        if r in P and P[r]["inst"]: add(p["doi"], P[r]["doi"], inst_label(list(p["allinst"]), p["inst"]), inst_label(list(P[r]["allinst"]), P[r]["inst"]), p["year"])
        elif r in refs: add(p["doi"], refs[r]["doi"], inst_label(list(p["allinst"]), p["inst"]), inst_label(refs[r]["insts"]), p["year"])
for t, cl in citers_of.items():
    if not P[t]["inst"]: continue
    for cid in cl:
        c = citers[cid]; add(c["doi"], P[t]["doi"], inst_label(c["insts"]), inst_label(list(P[t]["allinst"]), P[t]["inst"]), c["year"])
cit = pd.DataFrame(edges, columns=["source_doi", "target_doi", "source_inst", "target_inst", "year"])
cit.to_csv(f"{OUT}/citation_network.csv", index=False)

# ---- authorship network (file) ----
ae, skipped = [], 0
for p in P.values():
    if not p["inst"]: continue
    if p["n_auth"] > MAX_AUTH: skipped += 1; continue
    for a, b in itertools.combinations(p["auths"], 2):
        if not (a["mine"] or b["mine"]): continue
        ae.append({"author_a": a["name"], "author_b": b["name"], "paper_doi": p["doi"],
                   "inst_a": inst_label(a["insts"], a["mine"]), "inst_b": inst_label(b["insts"], b["mine"]), "year": p["year"]})
aut = pd.DataFrame(ae, columns=["author_a", "author_b", "paper_doi", "inst_a", "inst_b", "year"])
aut.to_csv(f"{OUT}/authorship_network.csv", index=False)

# ---- indian connections (file) ----
conn = C.defaultdict(lambda: [set(), 0])
for p in P.values():
    for name in p["inst"]:
        for partner in indian_others(p["allinst"], OWN_DISP[name]):
            conn[(name, partner)][0].add(p["id"])
for k, v in conn.items(): v[1] = sum(P[x]["cites"] for x in v[0])
ic = pd.DataFrame([{"your_inst": k[0], "partner_inst": k[1], "shared_papers": len(v[0]), "total_citations": v[1]}
                   for k, v in conn.items()], columns=["your_inst", "partner_inst", "shared_papers", "total_citations"]
                  ).sort_values(["your_inst", "shared_papers"], ascending=[True, False])
ic.to_csv(f"{OUT}/indian_connections.csv", index=False)

# ======================= METRICS =======================
SCOPES = NAMES + ["ALL"]
M = {"faculty_min_papers": FACULTY_MIN_PAPERS, "group": GROUP, "institutions": NAMES, "skipped_mega_papers": skipped,
     "per": {}, "has_quartiles": bool(Q), "mega_threshold": MAX_AUTH,
     "unattributed_papers": len(unattributed)}
hval = lambda aid: (authors.get(aid) or {}).get("h")
in_range = lambda p: bool(p["inst"]) and 2016 <= p["year"] <= 2026
def scope_papers(scope): return [p for p in P.values() if in_range(p) and (scope == "ALL" or scope in p["inst"])]

for name in SCOPES:
    ps = scope_papers(name)
    d = {"papers": len(ps), "citations": sum(p["cites"] for p in ps)}
    d["trend"] = {y: sum(1 for p in ps if p["year"] == y) for y in range(2016, 2027)}
    jq = [p for p in ps if p["type"] == "journal"]
    qc = C.Counter(p["quartile"] or "Unknown" for p in jq)
    d["quartiles"] = dict(qc)
    known = sum(v for k, v in qc.items() if k != "Unknown")
    d["q1_fraction"] = round(100 * qc.get("Q1", 0) / known, 1) if known else None
    d["top_journals"] = C.Counter(p["journal"] for p in ps if p["journal"]).most_common(5)
    d["fields"] = C.Counter(p["field"] for p in ps).most_common(12)
    d["conf"] = dict(C.Counter(p["quartile"] or "Unranked" for p in ps if p["type"] == "conference"))
    d["top_cited"] = [{"title": p["title"], "journal": p["journal"], "year": p["year"], "cites": p["cites"], "doi": p["doi"],
                       "n_authors": p["n_auth"]} for p in sorted(ps, key=lambda p: -p["cites"])[:10]]
    fac = {}
    for p in ps:
        for a in p["auths"]:
            if not a["mine"] or (name != "ALL" and name not in a["mine"]): continue
            f = fac.setdefault(a["id"], {"name": a["name"], "papers": 0, "cites": 0, "fields": C.Counter(), "journals": C.Counter(),
                                         "inst": name if name != "ALL" else a["mine"][0]})
            f["papers"] += 1; f["cites"] += p["cites"]; f["fields"][p["field"]] += 1
            if p["journal"]: f["journals"][p["journal"]] += 1
    fl = [{"name": f["name"], "inst": f["inst"], "dept": f["fields"].most_common(1)[0][0], "h": hval(k), "papers": f["papers"],
           "cites": f["cites"], "top_journal": (f["journals"].most_common(1) or [("", 0)])[0][0]} for k, f in fac.items()]
    d["authors_all"] = len(fl)
    fl = [f for f in fl if f["papers"] >= FACULTY_MIN_PAPERS]
    d["faculty"] = sorted(fl, key=lambda f: -(f["h"] or 0))
    hs = [f["h"] for f in fl if f["h"] is not None]
    bins = list(range(0, 85, 5))
    d["h_hist"] = [sum(1 for h in hs if b <= h < b + 5) for b in bins[:-1]]; d["h_bins"] = [f"{b}-{b+4}" for b in bins[:-1]]
    d["h_median"] = float(pd.Series(hs).median()) if hs else None
    M["per"][name] = d

# ---- networks and citation flow, computed PER SCOPE (each institution + whole cluster) ----
def cit_stats(scope):
    G = nx.DiGraph()
    for p in scope_papers(scope):
        G.add_node(p["id"], doi=p["doi"], title=p["title"], inst=scope if scope != "ALL" else p["inst"][0],
                   cites=p["cites"], quartile=p.get("quartile"))
    for p in P.values():
        if p["id"] in G:
            for r in p["refs"]:
                if r in G: G.add_edge(p["id"], r)
    pr = nx.pagerank(G) if G.number_of_edges() else {n: 0 for n in G}
    indeg = dict(G.in_degree())

    # ---- Quality-Weighted PageRank ----
    # Weight = quartile of the CITED paper (target). Being cited counts more
    # if the cited paper itself is in a top journal — amplifies prestige signal.
    # (Using citing paper's Q would be ~uniform since 76% are Q1.)
    QWEIGHT = {"Q1": 5, "Q2": 3, "Q3": 2, "Q4": 1}
    Gw = nx.DiGraph()
    Gw.add_nodes_from(G.nodes(data=True))
    for u, v in G.edges:
        cited_q = G.nodes[v].get("quartile") or ""   # v = the paper being cited
        w = QWEIGHT.get(cited_q, 1)
        Gw.add_edge(u, v, weight=w)
    wpr = nx.pagerank(Gw, weight="weight") if Gw.number_of_edges() else {n: 0 for n in Gw}

    # Rank positions for comparison
    pr_ranks = {n: i+1 for i, n in enumerate(sorted(pr, key=pr.get, reverse=True))}
    wpr_ranks = {n: i+1 for i, n in enumerate(sorted(wpr, key=wpr.get, reverse=True))}

    d = {"nodes": G.number_of_nodes(), "edges": G.number_of_edges(),
         "isolated": sum(1 for n in G if G.degree(n) == 0),
         "indeg_hist": dict(C.Counter(min(v, 10) for v in indeg.values())),
         "pagerank_top10": [{"title": G.nodes[n]["title"], "doi": G.nodes[n]["doi"], "inst": G.nodes[n]["inst"],
                             "pr": round(pr[n], 5), "in": indeg[n]} for n in sorted(pr, key=pr.get, reverse=True)[:10]],
         "qweighted_pagerank_top10": [{"title": G.nodes[n]["title"], "doi": G.nodes[n]["doi"], "inst": G.nodes[n]["inst"],
                                       "wpr": round(wpr[n], 5), "pr": round(pr[n], 5), "in": indeg[n],
                                       "rank_change": pr_ranks.get(n, 0) - wpr_ranks.get(n, 0)}
                                      for n in sorted(wpr, key=wpr.get, reverse=True)[:10]]}
    if scope == "ALL":
        d["flow_matrix"] = {a: {b: 0 for b in NAMES} for a in NAMES}
        for u, v in G.edges: d["flow_matrix"][G.nodes[u]["inst"]][G.nodes[v]["inst"]] += 1
    keep = [n for n in sorted(G.nodes, key=lambda n: -G.degree(n)) if G.degree(n) > 0][:250]
    H = G.subgraph(keep)
    d["viz"] = {"nodes": [{"id": n, "label": (G.nodes[n]["title"] or "")[:70], "inst": G.nodes[n]["inst"], "v": indeg[n] + 1} for n in H],
                "edges": [{"from": u, "to": v} for u, v in H.edges]}
    return d

def auth_stats(scope):
    A = nx.Graph()
    for p in scope_papers(scope):
        if p["n_auth"] > MAX_AUTH: continue
        mine = [a for a in p["auths"] if a["mine"] and (scope == "ALL" or scope in a["mine"])]
        for a in mine: A.add_node(a["id"], name=a["name"], inst=scope if scope != "ALL" else a["mine"][0])
        for a, b in itertools.combinations(mine, 2):
            if a["id"] == b["id"]: continue
            w_ = A.get_edge_data(a["id"], b["id"], {"weight": 0})["weight"]
            A.add_edge(a["id"], b["id"], weight=w_ + 1)
    n = A.number_of_nodes()
    dc = nx.degree_centrality(A) if n > 1 else {}
    bc = nx.betweenness_centrality(A, k=min(400, n), seed=1) if n > 1 else {}
    comms = nx.community.louvain_communities(A, seed=1) if A.number_of_edges() else []
    cid = {x: i for i, c in enumerate(sorted(comms, key=len, reverse=True)) for x in c}
    top = lambda dd: [{"name": A.nodes[x]["name"], "inst": A.nodes[x]["inst"], "v": round(dd[x], 4), "deg": A.degree(x)}
                      for x in sorted(dd, key=dd.get, reverse=True)[:10]]
    comp = sorted((len(c) for c in nx.connected_components(A)), reverse=True) if n else []
    d = {"nodes": n, "edges": A.number_of_edges(), "isolated": sum(1 for x in A if A.degree(x) == 0),
         "cross_inst_edges": sum(1 for u, v in A.edges if A.nodes[u]["inst"] != A.nodes[v]["inst"]),
         "components": len(comp), "giant_component": comp[0] if comp else 0,
         "communities": len([c for c in comms if len(c) > 1]), "largest_communities": sorted((len(c) for c in comms), reverse=True)[:8],
         "modularity": round(nx.community.modularity(A, comms), 3) if comms else None,
         "deg_top10": top(dc), "btw_top10": top(bc)}
    keep = [x for x in sorted(A.nodes, key=lambda x: -A.degree(x)) if A.degree(x) > 0][:250]
    H = A.subgraph(keep)
    d["viz"] = {"nodes": [{"id": x, "label": A.nodes[x]["name"], "inst": A.nodes[x]["inst"], "group": cid.get(x, 0), "v": A.degree(x)} for x in H],
                "edges": [{"from": u, "to": v, "value": dd["weight"]} for u, v, dd in H.edges(data=True)]}
    return d

def flow_stats(scope):
    """Citation LINKS (citing work -> cited paper of ours) to/from Indian institutes OUTSIDE the scope.
    scope = one institution: 'outside' = every other institution incl. the other 3 in the group.
    scope = ALL: 'outside' = anything other than the 4 assigned institutions."""
    inflow, outflow, yin, yout = C.Counter(), C.Counter(), C.Counter(), C.Counter()
    n_in = n_out = 0
    for p in scope_papers(scope):
        excl = set().union(*OWN_DISP.values()) if scope == "ALL" else OWN_DISP[scope]
        for cid_ in citers_of[p["id"]]:
            o = indian_others(citers[cid_]["insts"], excl)
            if o:
                n_in += 1; yin[citers[cid_]["year"]] += 1
                for x in o: inflow[x] += 1
        for r in set(p["refs"]):
            ins = P[r]["allinst"] if r in P else (refs[r]["insts"] if r in refs else [])
            o = indian_others(ins, excl)
            if o:
                n_out += 1; yout[p["year"]] += 1
                for x in o: outflow[x] += 1
    return {"in": n_in, "out": n_out, "ratio": round(n_in / n_out, 2) if n_out else None,
            "in_top10": inflow.most_common(10), "out_top10": outflow.most_common(10),
            "year_in": {y: yin.get(y, 0) for y in range(2016, 2027)}, "year_out": {y: yout.get(y, 0) for y in range(2016, 2027)}}

M["net"] = {sc: {"cit": cit_stats(sc), "auth": auth_stats(sc), "flow": flow_stats(sc)} for sc in SCOPES}
# legacy keys (cluster level) used by the report
M["citnet"], M["authnet"], M["flow"] = M["net"]["ALL"]["cit"], M["net"]["ALL"]["auth"], dict(M["net"]["ALL"]["flow"])
M["flow"]["per_inst"] = {n: M["net"][n]["flow"] for n in NAMES}

# ---- connectivity map: partner institutes, cross-cluster flag, topic overlap ----
def cluster_of(n):
    n = n.lower()
    for ks, lab in [(("indian institute of technology",), "IIT"),
                    (("iiser", "indian institute of science education"), "IISER"),
                    (("council of scientific", "csir", "national chemical laboratory", "indian institute of chemical"), "CSIR"),
                    (("atomic energy", "bhabha", "variable energy cyclotron", "raja ramanna", "plasma research", "saha institute",
                      "institute of mathematical sciences", "harish-chandra", "national institute of science education and research",
                      "institute of physics"), "DAE"),
                    (("tata institute", "indian institute of science"), "TIFR/IISc"),
                    (("national institute of technology",), "NIT"),
                    (("indian institute of information technology", "international institute of information"), "IIIT"),
                    (("indian statistical",), "ISI"),
                    (("university", "college", "universit"), "University")]:
        if any(k in n for k in ks): return lab
    return "Other"
topics = {name: {p["subfield"] for p in scope_papers(name)} for name in NAMES}
cc = []
for name in NAMES:
    for (nm, partner), v in sorted(((k, v) for k, v in conn.items() if k[0] == name), key=lambda kv: -len(kv[1][0]))[:25]:
        ptop = {P[x]["subfield"] for x in v[0]}
        j = len(topics[name] & ptop) / len(topics[name] | ptop) if topics[name] | ptop else 0
        cc.append({"inst": name, "partner": partner, "shared": len(v[0]), "cites": v[1], "cluster": cluster_of(partner), "jaccard": round(j, 3)})
M["connections"] = cc
M["partner_count"] = {n: sum(1 for k in conn if k[0] == n) for n in NAMES}
M["generated_from"] = {"works": len(works), "attributed_papers": len(P) - len(unattributed), "rows": len(df),
                       "citation_edges": len(cit), "author_edges": len(aut)}
json.dump(M, open(f"{OUT}/metrics.json", "w"), default=str)
print("OK", M["generated_from"])
