#!/usr/bin/env python3
"""Step 3 - interactive dashboard: out/dashboard.html (self-contained, works offline)."""
import csv, json, os, collections as C
from journal_if import impact_factor, if_band
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUT_DIR") or os.path.join(HERE, "out")
M = json.load(open(f"{OUT}/metrics.json"))
DEMO = "DEMO" if "DEMO_OUTPUT_synthetic" in OUT else ""

# Impact-factor buckets from the paper CSV (does not re-run network analysis), for every author-count mode.
_csv = os.path.join(OUT, f"group{M.get('group', 23)}_data.csv")
CUT = M.get("team_cut", 10)
MODE_OK = {"all": lambda n: True, "lt10": lambda n: n < CUT, "ge10": lambda n: n >= CUT}
PAPERS, ALL_PAPERS = [], []
_seen_inst, _seen_doi = set(), set()
if os.path.exists(_csv):
    with open(_csv, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ifv = impact_factor(row.get("issn"))
            rec = {"inst": row.get("institution"), "journal": row.get("journal_name") or "",
                   "ifv": ifv, "band": if_band(ifv), "n": int(row.get("n_authors") or 0)}
            k_inst = (row.get("doi") or row.get("title"), rec["inst"])
            if k_inst not in _seen_inst:
                _seen_inst.add(k_inst)
                PAPERS.append(rec)
            k_doi = row.get("doi") or row.get("title")
            if k_doi not in _seen_doi:
                _seen_doi.add(k_doi)
                ALL_PAPERS.append(rec)

def _stats_from(rows):
    bands = C.Counter(p["band"] for p in rows)
    gt10 = bands.get("gt10", 0)
    journals = {}
    for p in rows:
        if p["ifv"] and p["ifv"] > 5 and p["journal"]:
            j = journals.setdefault(p["journal"], {"journal": p["journal"], "ifv": p["ifv"], "n": 0})
            j["n"] += 1
    top = sorted(journals.values(), key=lambda x: (-x["ifv"], -x["n"]))[:12]
    return {"if_bins": {"IF > 10": bands.get("gt10", 0), "IF 5–10": bands.get("gt5", 0),
                        "IF ≤ 5": bands.get("lt5", 0), "Unlisted": bands.get("unlisted", 0)},
            "if_gt5": bands.get("gt5", 0) + gt10, "if_gt10": gt10, "if_journals": top}

for mk, MM in (M.get("modes") or {"all": {"per": M["per"]}}).items():
    ok = MODE_OK.get(mk, MODE_OK["all"])
    for name in MM["per"]:
        rows = ALL_PAPERS if name == "ALL" else [p for p in PAPERS if p["inst"] == name]
        MM["per"][name].update(_stats_from([p for p in rows if ok(p["n"])]))
# the top-level copy (= all papers) is only used by report.py; drop it to keep the dashboard small
for k in ("per", "net", "connections", "partner_count", "citnet", "authnet", "flow"): M.pop(k, None)

# Colour citation-network nodes by IF without recomputing the graph
RAW = os.environ.get("RAW_DIR") or os.path.join(HERE, "raw")
_id2issn = {}
_wp = os.path.join(RAW, "works.json")
if os.path.exists(_wp):
    for w in json.load(open(_wp)):
        src = (w.get("primary_location") or {}).get("source") or {}
        _id2issn[w["id"].split("/")[-1]] = src.get("issn_l") or ((src.get("issn") or [None])[0])
for N in [N for MM in M["modes"].values() for N in MM["net"].values()]:
    for n in (N.get("cit") or {}).get("viz", {}).get("nodes", []):
        ifv = impact_factor(_id2issn.get(n.get("id"), ""))
        n["ifv"] = ifv
        n["band"] = if_band(ifv)

HTML = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>DPCN Group 23 Dashboard</title>
<script>__CHARTJS__</script>
<script>__VIS__</script>
<style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#1b2430;--mut:#64707e;--line:#e3e7ec;--acc:#2a5bd7}
@media(prefers-color-scheme:dark){:root{--bg:#10151c;--card:#182029;--ink:#e8edf3;--mut:#93a0ae;--line:#27323d;--acc:#6f95ff}}
*{box-sizing:border-box}body{margin:0;font:14px/1.45 system-ui,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--ink)}
header{padding:20px 24px 8px}h1{margin:0;font-size:22px}header p{margin:4px 0 0;color:var(--mut)}
.demo{background:#b3261e;color:#fff;padding:8px 24px;font-weight:600}
nav{display:flex;gap:8px;flex-wrap:wrap;padding:12px 24px;position:sticky;top:0;background:var(--bg);z-index:5}
nav button{border:1px solid var(--line);background:var(--card);color:var(--ink);padding:7px 14px;border-radius:20px;cursor:pointer;font:inherit}
nav button.on{background:var(--acc);color:#fff;border-color:var(--acc)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;padding:0 24px}
.kpi,.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.kpi b{display:block;font-size:24px}.kpi span{color:var(--mut);font-size:12px}
main{display:grid;grid-template-columns:repeat(auto-fit,minmax(420px,1fr));gap:14px;padding:14px 24px 40px}
.card h2{font-size:14px;margin:0 0 10px}.wide{grid-column:1/-1}
.card>canvas, .card div>canvas{max-height:280px}
.net{height:min(78vh,860px);border:1px solid var(--line);border-radius:8px;background:var(--bg);position:relative;overflow:hidden}
.net .vis-network{width:100%;height:100%}
.net canvas{max-height:none!important;width:100%!important;height:100%!important;display:block}
.net .vis-navigation{display:none!important}
.netbar{display:flex;flex-wrap:wrap;align-items:center;gap:8px 14px;margin:0 0 8px}
.chip{display:inline-flex;align-items:center;gap:6px;font-size:12px;color:var(--mut)}
.dot{width:10px;height:10px;border-radius:50%;display:inline-block}
.ifpill{display:inline-block;padding:2px 8px;border-radius:999px;font-size:11px;font-weight:600;margin-right:4px}
.ifpill.gt10{background:#f3e3a6;color:#6a5200}.ifpill.gt5{background:#c8efda;color:#0d5c38}
.ifpill.lt5{background:#dbe4ff;color:#1e3a8a}.ifpill.unlisted{background:#e8edf2;color:#5b6775}
@media(prefers-color-scheme:dark){
  .ifpill.gt10{background:#5c4a12;color:#f3e3a6}.ifpill.gt5{background:#164b34;color:#c8efda}
  .ifpill.lt5{background:#24356a;color:#c5d3ff}.ifpill.unlisted{background:#2a3440;color:#93a0ae}
}
table{border-collapse:collapse;width:100%;font-size:13px}th,td{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left}
th{cursor:pointer;color:var(--mut);position:sticky;top:0;background:var(--card)}.scroll{max-height:340px;overflow:auto}
input{padding:6px 10px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--ink);margin-bottom:8px;width:240px}
a{color:var(--acc)}.note{color:var(--mut);font-size:12px;margin-top:6px}
#modes{padding-top:0}#modes span{color:var(--mut);font-size:12px;align-self:center;margin-right:4px}
.flag{display:inline-block;background:#fde7d9;color:#8a3a0c;border-radius:6px;padding:1px 6px;margin:1px 2px 1px 0;font-size:11px}
.st{display:inline-block;border-radius:6px;padding:1px 6px;font-size:11px;font-weight:600;background:#e8edf2;color:#5b6775}
.st.fac{background:#c8efda;color:#0d5c38}.st.no{background:#fde2e1;color:#8c1d18}
@media(prefers-color-scheme:dark){.flag{background:#4a2a14;color:#fbd3b5}.st{background:#2a3440;color:#93a0ae}.st.fac{background:#164b34;color:#c8efda}.st.no{background:#4d1d1b;color:#f6c4c1}}
select{padding:6px 10px;border:1px solid var(--line);border-radius:6px;background:var(--card);color:var(--ink);margin:0 0 8px 8px}
td.t{max-width:380px}
@media(max-width:600px){main{grid-template-columns:1fr}.net{height:70vh}}
</style></head><body>
__DEMO__
<header><h1>DPCN Research Mapping · Group 23</h1><p>S.N. Bose Centre · Bose Institute · SINP (Kolkata) + NCBS Bangalore · publications 2016–2026 · source: OpenAlex</p></header>
<nav id="tabs"></nav><nav id="modes"><span>Papers by number of authors:</span></nav><div class="kpis" id="kpis"></div><main id="main"></main>
<footer style="padding:0 24px 30px;color:var(--mut);font-size:12px">Data notes: source is OpenAlex. Faculty status is matched by name against the official faculty pages of NCBS, SN Bose Centre, Bose Institute and SINP (fetch_faculty.py) plus manual checks (faculty_checks.csv). Impact factors are approximate 2023 JCR values; quartiles from Scimago. “< 10 authors” discards every paper with 10 or more authors. OpenAlex can merge authors with common initial-style names, so some h-index values may be inflated. A few papers list a repository (e.g. RECERCAT) instead of a journal. 2025–26 counts are incomplete.</footer>
<script>
const M=__DATA__;const COL=['#2a5bd7','#e8743b','#19a974','#a463f2','#d6336c','#8d6e63'];
const instColor={};M.institutions.forEach((n,i)=>instColor[n]=COL[i]);
let cur='ALL',mode='all',charts=[],nets=[];
const FAC_CATS=['Faculty','Emeritus','Adjunct faculty','Former faculty','PhD supervisor (current/former faculty)'];
const stPill=s=>`<span class="st ${FAC_CATS.includes(s)?'fac':(s.startsWith('Not')?'no':'')}">${s}</span>`;
const flags=f=>(f||[]).map(x=>`<span class="flag">${x}</span>`).join('');
const fmtIF=v=>v==null?'–':v;
const $=(h)=>{const d=document.createElement('div');d.innerHTML=h;return d.firstElementChild};
function card(t,body,cls=''){return `<div class="card ${cls}"><h2>${t}</h2>${body}</div>`}
function table(id,cols,rows){return `<div class="scroll"><table id="${id}"><thead><tr>${cols.map((c,i)=>`<th data-i="${i}">${c} ⇅</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${r.map(x=>`<td>${x??'–'}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`}
function sortable(id){const t=document.getElementById(id);if(!t)return;t.querySelectorAll('th').forEach(th=>th.onclick=()=>{const i=+th.dataset.i,dir=th.dir=-(th.dir||-1);const b=t.tBodies[0];[...b.rows].sort((x,y)=>{let a=x.cells[i].innerText,c=y.cells[i].innerText;const na=parseFloat(a),nc=parseFloat(c);return (isNaN(na)||isNaN(nc)?a.localeCompare(c):na-nc)*dir}).forEach(r=>b.appendChild(r))})}
function chart(id,cfg){const el=document.getElementById(id);if(!el){console.warn('skip',id);return}charts.push(new Chart(el,cfg))}
function render(){
 charts.forEach(c=>c.destroy());charts=[];nets.forEach(n=>n.destroy());nets=[];
 const MM=M.modes[mode],d=MM.per[cur],isAll=cur==='ALL',N=MM.net[cur],CN=N.cit,AN=N.auth,FL=N.flow;
 document.querySelectorAll('#tabs button').forEach(b=>b.classList.toggle('on',b.dataset.k===cur));
 document.querySelectorAll('#modes button').forEach(b=>b.classList.toggle('on',b.dataset.k===mode));
 const q1=d.q1_fraction==null?'n/a':d.q1_fraction+'%';
 document.getElementById('kpis').innerHTML=[['Papers ('+MM.label+')',d.papers],['Citations',d.citations.toLocaleString()],['Verified faculty (official lists)',d.faculty_verified],['Authors ≥'+M.faculty_min_papers+' papers',d.faculty.length],['Q1 & IF > 10',d.tier_counts['Q1 & IF>10']],['Q1 & IF > 5',d.tier_counts['Q1 & IF>5']],['Q1 share',q1],['Median h-index',d.h_median??'–'],['IF > 5',(d.if_gt5??0).toLocaleString()],['IF > 10',(d.if_gt10??0).toLocaleString()]].map(([a,b])=>`<div class="kpi"><b>${b}</b><span>${a}</span></div>`).join('');
 const qk=Object.keys(d.quartiles),ck=Object.keys(d.conf);
 const fl=d.faculty;
 document.getElementById('main').innerHTML=
  card('Publication trend 2016–2026','<canvas id="c_trend"></canvas>')+
  card('Journal quartile distribution',qk.length===1&&qk[0]==='Unknown'?'<p class="note">Quartiles not loaded. Put Scimago&#39;s scimago.csv in the group23 folder and re-run build.py, dashboard.py and report.py.</p>':'<canvas id="c_q"></canvas>')+
  card('Journal impact factor — IF > 5 and IF > 10','<canvas id="c_if"></canvas><div class="note">IF > 5 includes IF > 10. Unlisted = journal not in the IF lookup (not assumed below 5). Values are approximate 2023 JCR impact factors.</div>')+
  card('High-IF journals we publish in (IF > 5)',table('t_ifj',['Journal','IF','Papers'],(d.if_journals||[]).map(j=>[`<span class="ifpill ${j.ifv>10?'gt10':'gt5'}">${j.ifv>10?'IF > 10':'IF > 5'}</span>${j.journal}`,j.ifv,j.n])))+
  card('Top 5 journals','<div style="height:300px"><canvas id="c_j"></canvas></div>')+
  card('h-index distribution of faculty','<canvas id="c_h"></canvas>')+
  card('Research area breakdown','<div style="height:420px"><canvas id="c_f"></canvas></div>')+
  card('Conference rank (CORE A*/A/B/C)',ck.some(k=>k!=='Unranked')?'<canvas id="c_conf"></canvas>':'<p class="note">'+(ck.length?(d.conf.Unranked+' conference paper(s) found, but no CORE ranks loaded (OpenAlex does not provide them).'):'No conference papers in this selection.')+'</p>')+
  card('Faculty list & performance — '+MM.label+' (click headers to sort)','<input id="fs" placeholder="Search name…"><select id="fst"><option value="">Everyone with ≥'+M.faculty_min_papers+' papers</option><option value="fac">Verified faculty only</option><option value="no">Not on official faculty list</option></select>'+table('t_fac',['Name','Institution','Status (official list)','Department (main field)','h-index','Papers','Citations','Most frequent journal','Best journal (Q1, highest IF)','Q1·IF>10 papers','Q1·IF>5 papers'],fl.map(f=>[f.name,f.inst,stPill(f.status),f.dept,f.h,f.papers,f.cites,f.top_journal,f.best_journal?f.best_journal+' ('+f.best_if+')':'–',f.n_a,f.n_ab]))+'<div class="note">Status comes from the institutes&#39; own People pages (current, emeritus, adjunct, former, visiting) plus manual checks. Verified faculty are listed even with fewer than '+M.faculty_min_papers+' papers. “Not on official list” = students, postdocs, visitors, outside collaborators — or faculty who retired before the current lists (SINP publishes no former-faculty list; for SN Bose, former faculty and former PhD students come from its official PhD-alumni list). h-index is OpenAlex&#39;s lifetime value and can be inflated when OpenAlex merges people with the same name.</div>','wide')+
  card('Best paper of each author — most-cited Q1 & IF>10 paper, else most-cited Q1 & IF>5 paper ('+MM.label+')','<input id="bs" placeholder="Search name…">'+table('t_best',['Name','Institution','Status','Tier','Best paper','Journal','IF','Year','Authors','Citations','Flags / checks'],fl.filter(f=>f.best).map(f=>[f.name,f.inst,stPill(f.status),f.best.tier==='A'?'<span class="ifpill gt10">Q1 · IF>10</span>':'<span class="ifpill gt5">Q1 · IF>5</span>',`<span class="t">${f.best.doi?`<a target=_blank href="${f.best.doi}">${f.best.t}</a>`:f.best.t}</span>`,f.best.j,f.best.if,f.best.y,f.best.n>=M.team_cut?`<b>${f.best.n}</b>`:f.best.n,f.best.c,flags(f.flags)+(f.note?`<div class="note">${f.note}</div>`:'')]))+'<div class="note">Every paper here carries the author&#39;s '+(isAll?'group-institute':cur)+' affiliation. Flags mark best papers with ≥'+M.team_cut+' authors, Q1·IF>10 records dominated by large-author papers, other affiliations listed on the best paper (work possibly done elsewhere), and merged OpenAlex profiles. Switch to “< '+M.team_cut+' authors” to see each person&#39;s best small-team paper.</div>','wide')+
  card('Top journals — Q1 & IF > 10 ('+MM.label+')',table('t_tj10',['Journal','IF','Papers'],d.tier_journals.gt10.map(j=>[j[0],j[1],j[2]])))+
  card('Top journals — Q1 & IF > 5 ('+MM.label+')',table('t_tj5',['Journal','IF','Papers'],d.tier_journals.gt5.map(j=>[j[0],j[1],j[2]])))+
  card('Most-cited papers (top '+M.top_cited_n+') — '+MM.label,table('t_top',['Title','Journal','Q','IF','Year','Citations','Authors','DOI'],d.top_cited.map(p=>[p.title,p.journal,p.quartile||'–',fmtIF(p.ifv),p.year,p.cites,p.n_authors>=M.team_cut?`<span class="flag">${p.n_authors} authors</span>`:p.n_authors,p.doi?`<a target=_blank href="${p.doi}">link</a>`:'–'])),'wide')+
  card('Citation network (node = paper, arrow = cites) — '+(isAll?'whole group':cur),'<div class="netbar"><span class="chip"><i class="dot" style="background:#c9a227"></i>IF > 10</span><span class="chip"><i class="dot" style="background:#19a974"></i>IF > 5</span><span class="chip"><i class="dot" style="background:#2a5bd7"></i>IF ≤ 5</span><span class="chip"><i class="dot" style="background:#9aa5b1"></i>Unlisted</span><span class="note" style="margin:0">Click a node to see its title · click empty space to hide it · hover for a tooltip · scroll to zoom · drag to pan.</span></div><div class="net" id="n_cit"></div><div class="note">Full-width view of the '+CN.viz.nodes.length+' best-connected papers. Full network: '+CN.nodes.toLocaleString()+' papers, '+CN.edges.toLocaleString()+' citation links ('+CN.isolated.toLocaleString()+' isolated). Fill = impact factor band; ring colour = institution.</div>','wide')+
  card('Authorship network (node = author, line = co-authored) — '+(isAll?'whole group':cur),'<div class="netbar"><span class="note" style="margin:0">Click a node to see the name · click empty space to hide it · hover for a tooltip · scroll to zoom · drag to pan.</span></div><div class="net" id="n_aut"></div><div class="note">Full-width view of the '+AN.viz.nodes.length+' most-connected authors. Full network: '+AN.nodes.toLocaleString()+' authors, '+AN.edges.toLocaleString()+' co-author links, '+AN.communities+' Louvain communities (modularity '+AN.modularity+'), giant component '+AN.giant_component+', '+AN.cross_inst_edges.toLocaleString()+' cross-institution links. Papers with more than '+M.mega_threshold+' authors are left out. Node colour = Louvain community.</div>','wide')+
  card('PageRank top 10 — most influential papers ('+(isAll?'whole group':cur)+')',table('t_pr',['Paper','Inst','PageRank','In-degree'],CN.pagerank_top10.map(p=>[p.title,p.inst,p.pr,p.in])))+
  card('🆕 Quality-Weighted PageRank — Q1-published papers get 5× citation weight, Q2=3×, Q3=2×, Q4=1×','<div class="note" style="margin-bottom:8px">Papers published in higher-quartile journals receive amplified citation weight. <b>Boost</b> shows % score change vs normal PageRank. Positive = paper benefits from being in a top journal.</div>'+table('t_wpr',['Paper','Inst','Weighted PR','Normal PR','In-deg','Boost'],(CN.qweighted_pagerank_top10||[]).map(p=>{let pct=p.pr>0?((p.wpr-p.pr)/p.pr*100).toFixed(1):'0';return [p.title,p.inst,p.wpr,p.pr,p.in,(pct>0?'+':'')+pct+'%']})),'wide')+
  card('Authorship: top brokers by betweenness',table('t_bc',['Author','Inst','Betweenness','Collaborators'],AN.btw_top10.map(p=>[p.name,p.inst,p.v,p.deg])))+card('Authorship: most collaborative (degree)',table('t_dg',['Author','Inst','Degree centrality','Collaborators'],AN.deg_top10.map(p=>[p.name,p.inst,p.v,p.deg])))+
  card('Citation flow with other Indian institutes by year','<canvas id="c_flow"></canvas><div class="note">In = citations our papers received from '+(isAll?'Indian institutes outside the 4':'Indian institutes other than '+cur+' (including the other three here)')+': '+FL.in.toLocaleString()+'. Out = citations our papers gave to them: '+FL.out.toLocaleString()+'. In/Out ratio '+(FL.ratio??'n/a')+'. Each citing paper → cited paper link is counted once, in the year of the citing paper.</div>')+card('Top 10 Indian institutes citing us',table('t_ci',['Institute','Citations to us','% via ≥'+M.team_cut+'-author papers'],FL.in_top10.map(x=>[x[0],x[1],(x[2]??'–')+'%']))+'<div class="note">A high % means the link comes from large collaborations (e.g. CMS/ALICE members citing collaboration papers), not from independent use of our work.</div>')+card('Top 10 Indian institutes we cite',table('t_co',['Institute','Citations from us'],FL.out_top10.map(x=>[x[0],x[1]])))+
  card('Indian connectivity — partner institutes by shared papers (top 25 per institution). Cluster = type of partner; Jaccard = share of our research subfields that appear in the joint papers',table('t_cn',['Your inst','Partner','Shared papers','Citations','Cluster','Topic overlap (Jaccard)'],MM.connections.filter(c=>isAll||c.inst===cur).map(c=>[c.inst,c.partner,c.shared,c.cites,c.cluster,c.jaccard])));
 const yrs=Object.keys(d.trend);const base={responsive:true,plugins:{legend:{display:false}}};
 chart('c_trend',{type:'bar',data:{labels:yrs,datasets:[{data:Object.values(d.trend),backgroundColor:'#2a5bd7'}]},options:base});
 chart('c_q',{type:'doughnut',data:{labels:qk,datasets:[{data:qk.map(k=>d.quartiles[k]),backgroundColor:['#19a974','#2a5bd7','#e8743b','#d6336c','#9aa5b1']}]},options:{plugins:{legend:{position:'right'}}}});
 const ik=Object.keys(d.if_bins||{});
 if(ik.length)chart('c_if',{type:'doughnut',data:{labels:ik,datasets:[{data:ik.map(k=>d.if_bins[k]),backgroundColor:['#c9a227','#19a974','#2a5bd7','#9aa5b1']}]},options:{plugins:{legend:{position:'right'}}}});
 chart('c_j',{type:'bar',data:{labels:d.top_journals.map(j=>j[0]),datasets:[{data:d.top_journals.map(j=>j[1]),backgroundColor:'#a463f2'}]},options:{...base,indexAxis:'y',maintainAspectRatio:false,scales:{y:{type:'category',ticks:{autoSkip:false,callback:function(v){const l=this.getLabelForValue(v);return l.length>38?l.slice(0,37)+'…':l}}},x:{type:'linear',beginAtZero:true}}}});
 chart('c_h',{type:'bar',data:{labels:d.h_bins,datasets:[{data:d.h_hist,backgroundColor:'#19a974'}]},options:base});
 chart('c_f',{type:'bar',data:{labels:d.fields.map(j=>j[0]),datasets:[{data:d.fields.map(j=>j[1]),backgroundColor:'#e8743b'}]},options:{...base,indexAxis:'y',maintainAspectRatio:false,scales:{y:{type:'category',ticks:{autoSkip:false,callback:function(v){const l=this.getLabelForValue(v);return l.length>38?l.slice(0,37)+'…':l}}},x:{type:'linear',beginAtZero:true}}}});
 if(ck.some(k=>k!=='Unranked'))chart('c_conf',{type:'bar',data:{labels:ck,datasets:[{data:ck.map(k=>d.conf[k]),backgroundColor:'#8d6e63'}]},options:base});
 const ys=Object.keys(FL.year_in);
 chart('c_flow',{type:'line',data:{labels:ys,datasets:[{label:'In-flow',data:Object.values(FL.year_in),borderColor:'#2a5bd7'},{label:'Out-flow',data:Object.values(FL.year_out),borderColor:'#e8743b'}]},options:{responsive:true}});
 ['t_fac','t_best','t_tj10','t_tj5','t_top','t_pr','t_bc','t_dg','t_ci','t_co','t_cn','t_ifj'].forEach(sortable);
 const facFilter=()=>{const v=document.getElementById('fs').value.toLowerCase(),st=document.getElementById('fst').value;[...document.getElementById('t_fac').tBodies[0].rows].forEach(r=>{const s=r.cells[2].innerText,isF=FAC_CATS.includes(s.trim());r.style.display=r.cells[0].innerText.toLowerCase().includes(v)&&(!st||(st==='fac'?isF:!isF))?'':'none'})};
 document.getElementById('fs').oninput=facFilter;document.getElementById('fst').onchange=facFilter;
 document.getElementById('bs').oninput=e=>{const v=e.target.value.toLowerCase();[...document.getElementById('t_best').tBodies[0].rows].forEach(r=>r.style.display=r.cells[0].innerText.toLowerCase().includes(v)?'':'none')};
 const PAL=['#2a5bd7','#e8743b','#19a974','#a463f2','#d6336c','#c9a227','#1b9aaa','#8d6e63','#6c757d','#ff6f91'];
 const IFC={gt10:'#c9a227',gt5:'#19a974',lt5:'#2a5bd7',unlisted:'#9aa5b1'};
 const mk=(el,viz,dir,byComm)=>{
  const names={};
  const nodes=viz.nodes.map(n=>{
    const short=(n.label||'').length>42?(n.label.slice(0,41)+'…'):(n.label||'');
    names[n.id]=short;
    const fill=byComm?PAL[(n.group||0)%PAL.length]:(IFC[n.band]||IFC.unlisted);
    const ring=instColor[n.inst]||'#888';
    const tip=n.label+(n.ifv?(' · IF '+n.ifv):'')+(n.inst?(' · '+n.inst):'');
    return {id:n.id,label:'',title:tip,value:n.v,font:{size:0},
      color:{background:fill,border:ring,highlight:{background:fill,border:'#1b2430'}}};
  });
  const edges=viz.edges.map(e=>({...e,arrows:dir?'to':undefined}));
  if(!nodes.length){document.getElementById(el).innerHTML='<p class="note" style="padding:12px">No connections to draw here.</p>';return}
  const box=document.getElementById(el);
  const ds=new vis.DataSet(nodes);
  const nw=new vis.Network(box,{nodes:ds,edges},{
    nodes:{shape:'dot',font:{size:0,face:'system-ui',strokeWidth:3,strokeColor:'#fff',color:'#1b2430'},
      scaling:{min:8,max:36,label:{enabled:false}},borderWidth:2},
    edges:{color:{opacity:.32},smooth:false,width:1},
    physics:{stabilization:{iterations:280,fit:true},barnesHut:{gravitationalConstant:-12000,springLength:140}},
    interaction:{hover:true,tooltipDelay:80,navigationButtons:false,keyboard:true,zoomView:true}
  });nets.push(nw);
  let shown=null;
  nw.on('click',ev=>{
    const id=ev.nodes[0]||null;
    const changes=[];
    if(shown && shown!==id) changes.push({id:shown,label:'',font:{size:0}});
    if(id) changes.push({id,label:names[id]||'',font:{size:16,face:'system-ui',strokeWidth:4,strokeColor:'#fff',color:'#1b2430'}});
    if(changes.length) ds.update(changes);
    shown=id;
  });
  const sizeFit=()=>{nw.setSize(box.clientWidth+'px',box.clientHeight+'px');nw.redraw();nw.fit({padding:40})};
  nw.once('stabilizationIterationsDone',()=>{nw.setOptions({physics:false});sizeFit()});
  requestAnimationFrame(sizeFit);
 };
 mk('n_cit',CN.viz,true,false);mk('n_aut',AN.viz,false,true);
}
const tabs=document.getElementById('tabs');
['ALL',...M.institutions].forEach(k=>{const b=document.createElement('button');b.textContent=k==='ALL'?'All 4 institutions':k;b.dataset.k=k;b.onclick=()=>{cur=k;render()};tabs.appendChild(b)});
const mbar=document.getElementById('modes');
Object.entries(M.modes).forEach(([k,v])=>{const b=document.createElement('button');b.textContent=v.label;b.dataset.k=k;b.onclick=()=>{mode=k;render()};mbar.appendChild(b)});
render();
</script></body></html>"""
demo = '<div class="demo">DEMO – synthetic test data, NOT real publications. Re-run the pipeline on real OpenAlex data before submitting.</div>' if DEMO else ""
lib = lambda f: open(os.path.join(HERE, "lib", f)).read().replace("</script", "<\\/script")
open(f"{OUT}/dashboard.html", "w").write(HTML.replace("__CHARTJS__", lib("chart.js")).replace("__VIS__", lib("vis-network.js")).replace("__DATA__", json.dumps(M, default=str)).replace("__DEMO__", demo))
print("dashboard.html written")
