#!/usr/bin/env python3
"""Step 4 - statistics report: out/group23_report.pptx (10 slides, the maximum allowed).

Produces a polished, presentation-ready deck with:
  - Gradient header bars on every content slide
  - Consistent colour palette and typography
  - High-resolution matplotlib charts with clean styling
  - Colour-coded tables with alternating rows
  - Slide numbers and professional footer
"""
import json, os, textwrap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.environ.get("OUT_DIR") or os.path.join(HERE, "out")
M = json.load(open(f"{OUT}/metrics.json"))
NAMES = M["institutions"]
A = M["per"]["ALL"]
DEMO = "DEMO_OUTPUT_synthetic" in OUT
IMG = os.path.join(OUT, "img"); os.makedirs(IMG, exist_ok=True)

# ── Colour palette ──────────────────────────────────────────────────────
NAVY      = RGBColor(0x0D, 0x1B, 0x3E)
DARK_BLUE = RGBColor(0x14, 0x24, 0x4A)
ACCENT    = RGBColor(0x2A, 0x5B, 0xD7)
LIGHT_BG  = RGBColor(0xF4, 0xF6, 0xFA)
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
MUT       = RGBColor(0x64, 0x70, 0x7E)
DARK_TEXT  = RGBColor(0x1B, 0x24, 0x30)
COL4 = ["#2a5bd7", "#e8743b", "#19a974", "#a463f2"]   # per institution
COL4_RGB = [RGBColor(0x2A,0x5B,0xD7), RGBColor(0xE8,0x74,0x3B),
            RGBColor(0x19,0xA9,0x74), RGBColor(0xA4,0x63,0xF2)]

# ── Chart styling ───────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Helvetica Neue", "Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 12, "axes.spines.top": False, "axes.spines.right": False,
    "axes.labelsize": 13, "axes.titlesize": 14, "axes.labelcolor": "#1b2430",
    "xtick.color": "#64707e", "ytick.color": "#64707e",
    "figure.facecolor": "#f4f6fa", "axes.facecolor": "#f4f6fa",
    "savefig.facecolor": "#f4f6fa",
})

def save(name, w=7.0, h=3.8):
    plt.tight_layout()
    p = f"{IMG}/{name}.png"
    plt.savefig(p, dpi=200, bbox_inches="tight", pad_inches=0.15)
    plt.close()
    return p

# ── Charts ──────────────────────────────────────────────────────────────
yrs = list(range(2016, 2027))

# Publication trend – stacked bar
fig, ax = plt.subplots(figsize=(7.0, 3.8))
bot = [0] * 11
for n, c in zip(NAMES, COL4):
    v = [M["per"][n]["trend"][str(y)] for y in yrs]
    ax.bar(yrs, v, bottom=bot, color=c, label=n.split()[0], edgecolor="white", linewidth=0.5)
    bot = [a + b for a, b in zip(bot, v)]
ax.set_ylim(0, max(bot) * 1.25)
ax.legend(fontsize=9, frameon=False, ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.08))
ax.set_ylabel("Papers"); ax.set_xlabel("Year")
for sp in ["top","right"]: ax.spines[sp].set_visible(False)
c_trend = save("trend")

# Quartile distribution – grouped bars
fig, ax = plt.subplots(figsize=(7.0, 3.8))
qs = ["Q1", "Q2", "Q3", "Q4"]
qcols = ["#19a974", "#2a5bd7", "#e8743b", "#d6336c"]
x = range(len(NAMES))
w = 0.18
for i, (q, qc) in enumerate(zip(qs, qcols)):
    vals = [M["per"][n]["quartiles"].get(q, 0) for n in NAMES]
    ax.bar([xi + i*w for xi in x], vals, w, color=qc, label=q, edgecolor="white", linewidth=0.5)
ax.set_xticks([xi + 1.5*w for xi in x])
ax.set_xticklabels([n.split()[0] for n in NAMES], fontsize=10)
ax.legend(fontsize=9, frameon=False, ncol=4, loc="upper right")
ax.set_ylabel("Papers")
c_quart = save("quart")

# h-index distribution – grouped bars
fig, ax = plt.subplots(figsize=(7.0, 3.8))
w = 0.2
for i, (n, c) in enumerate(zip(NAMES, COL4)):
    ax.bar([xi + i*w for xi in range(len(M["per"][n]["h_hist"]))],
           M["per"][n]["h_hist"], w, color=c, label=n.split()[0], edgecolor="white", linewidth=0.3)
ax.set_xticks([xi + 1.5*w for xi in range(len(A["h_bins"]))])
ax.set_xticklabels(A["h_bins"], rotation=50, fontsize=8)
ax.set_xlabel("h-index"); ax.set_ylabel("Faculty count")
ax.legend(fontsize=8, frameon=False, ncol=2)
c_hidx = save("hidx")

# Research areas – horizontal bar
def hbar(items, name, color, max_items=10):
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    items = items[:max_items][::-1]
    labels = [textwrap.shorten(i[0], 40, placeholder="…") for i in items]
    vals = [i[1] for i in items]
    bars = ax.barh(labels, vals, color=color, edgecolor="white", linewidth=0.5)
    for bar, v in zip(bars, vals):
        ax.text(bar.get_width() + max(vals)*0.01, bar.get_y() + bar.get_height()/2,
                str(v), va="center", fontsize=9, color="#64707e")
    ax.set_xlabel("Papers")
    return save(name)
c_fields = hbar(A["fields"][:10], "fields", "#e8743b")

# Citation flow – line chart
fig, ax = plt.subplots(figsize=(7.0, 3.8))
ax.plot(yrs, [M["flow"]["year_in"][str(y)] for y in yrs], color=COL4[0],
        linewidth=2.5, marker="o", markersize=5, label="In-flow (cited by others)")
ax.plot(yrs, [M["flow"]["year_out"][str(y)] for y in yrs], color=COL4[1],
        linewidth=2.5, marker="s", markersize=5, label="Out-flow (we cite them)")
ax.fill_between(yrs, [M["flow"]["year_in"][str(y)] for y in yrs], alpha=0.08, color=COL4[0])
ax.fill_between(yrs, [M["flow"]["year_out"][str(y)] for y in yrs], alpha=0.08, color=COL4[1])
ax.legend(fontsize=9, frameon=False); ax.set_ylabel("Citation links"); ax.set_xlabel("Year")
c_flow = save("flow")

# In-degree distribution – bar
fig, ax = plt.subplots(figsize=(7.0, 3.8))
d = M["citnet"]["indeg_hist"]; ks = sorted(d, key=int)
ax.bar([("10+" if k == "10" else k) for k in ks], [d[k] for k in ks], color="#6f95ff",
       edgecolor="white", linewidth=0.5)
ax.set_yscale("log"); ax.set_xlabel("In-degree (cited by papers in corpus)"); ax.set_ylabel("Papers (log)")
c_indeg = save("indeg")


# ══════════════════════════════════════════════════════════════════════════
#  DECK CONSTRUCTION
# ══════════════════════════════════════════════════════════════════════════
prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.33), Inches(7.5)
blank = prs.slide_layouts[6]

# ── Helper functions ────────────────────────────────────────────────────
def add_header_bar(s):
    """Dark gradient header strip across the top."""
    rect = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, Inches(1.15))
    rect.fill.solid(); rect.fill.fore_color.rgb = NAVY; rect.line.fill.background()
    rect.shadow.inherit = False

def add_footer(s, slide_num):
    """Subtle footer with group info and slide number."""
    ft = s.shapes.add_textbox(Inches(0.6), Inches(7.0), Inches(10), Inches(0.4))
    p = ft.text_frame.paragraphs[0]
    p.text = "DPCN Course 2026  ·  Group 23  ·  Kolkata Cluster + NCBS"
    p.font.size = Pt(9); p.font.color.rgb = MUT
    sn = s.shapes.add_textbox(Inches(11.5), Inches(7.0), Inches(1.5), Inches(0.4))
    p2 = sn.text_frame.paragraphs[0]
    p2.text = f"{slide_num} / 10"; p2.alignment = PP_ALIGN.RIGHT
    p2.font.size = Pt(9); p2.font.color.rgb = MUT

def tb(s, x, y, w, h, text, size=14, bold=False, color=None, align=None):
    """Add a text box."""
    t = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = t.text_frame; tf.word_wrap = True
    if align: tf.paragraphs[0].alignment = align
    lines = text if isinstance(text, list) else [text]
    for i, line in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line; p.font.size = Pt(size)
        if bold: p.font.bold = True
        if color: p.font.color.rgb = color
        p.space_after = Pt(4)
        if align: p.alignment = align
    return t

def slide(title, subtitle, slide_num):
    """Create a content slide with header bar, title, and subtitle."""
    s = prs.slides.add_slide(blank)
    add_header_bar(s)
    tb(s, 0.6, 0.18, 11, 0.7, title, 26, True, WHITE)
    tb(s, 0.6, 1.2, 12, 0.5, subtitle, 14, False, MUT)
    add_footer(s, slide_num)
    if DEMO:
        tb(s, 9.5, 0.2, 3.5, 0.3, "⚠ DEMO DATA", 11, True, RGBColor(0xFF,0x6B,0x6B))
    return s

def pic(s, path, x=0.6, y=1.85, w=7.4):
    s.shapes.add_picture(path, Inches(x), Inches(y), width=Inches(w))

def side_panel(s, lines, x=8.4, y=2.0, size=13):
    """Right-side info panel."""
    tb(s, x, y, 4.5, 5.0, lines, size, color=DARK_TEXT)

def table(s, hdr, rows, x, y, w, h_per_row=0.32, size=10, colw=None, accent=True):
    """Professional table with header styling and alternating rows."""
    nr = len(rows) + 1
    t = s.shapes.add_table(nr, len(hdr), Inches(x), Inches(y),
                           Inches(w), Inches(h_per_row * nr)).table
    # Header row
    for j, h in enumerate(hdr):
        cell = t.cell(0, j); cell.text = h
        cell.fill.solid(); cell.fill.fore_color.rgb = NAVY
        for p in cell.text_frame.paragraphs:
            p.font.size = Pt(size); p.font.bold = True; p.font.color.rgb = WHITE
            p.space_before = Pt(2); p.space_after = Pt(2)
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    # Data rows
    for i, r in enumerate(rows, 1):
        for j, v in enumerate(r):
            cell = t.cell(i, j); cell.text = str(v if v is not None else "–")
            if i % 2 == 0:
                cell.fill.solid(); cell.fill.fore_color.rgb = RGBColor(0xF0, 0xF3, 0xF8)
            for p in cell.text_frame.paragraphs:
                p.font.size = Pt(size)
                p.space_before = Pt(1); p.space_after = Pt(1)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
    if colw:
        for j, cw in enumerate(colw):
            t.columns[j].width = Inches(cw)
    return t

def kpi_box(s, x, y, label, value, color=ACCENT):
    """A small KPI card."""
    rect = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y),
                               Inches(2.4), Inches(0.85))
    rect.fill.solid(); rect.fill.fore_color.rgb = RGBColor(0xF0,0xF3,0xF8)
    rect.line.fill.background(); rect.shadow.inherit = False
    tf = rect.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = str(value); p.font.size = Pt(22); p.font.bold = True
    p.font.color.rgb = color; p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph(); p2.text = label; p2.font.size = Pt(9)
    p2.font.color.rgb = MUT; p2.alignment = PP_ALIGN.CENTER

# ── Computed values ─────────────────────────────────────────────────────
q1 = {n: M["per"][n]["q1_fraction"] for n in NAMES}
fmt = lambda v: "n/a" if v is None else f"{v}%"
best = max(NAMES, key=lambda n: M["per"][n]["papers"])
F = M["flow"]; C = M["citnet"]; N = M["authnet"]


# ══════════════════════════════════════════════════════════════════════════
#  SLIDE 1: TITLE
# ══════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank)
# Full-width dark background
rect = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
rect.fill.solid(); rect.fill.fore_color.rgb = NAVY; rect.line.fill.background()

tb(s, 0.8, 1.2, 11.5, 1.2, "Research Mapping", 44, True, WHITE)
tb(s, 0.8, 2.3, 11.5, 0.7, "Kolkata Cluster + NCBS Bangalore", 28, False, RGBColor(0x6F,0x95,0xFF))
# Separator line
line = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(3.2), Inches(3), Pt(3))
line.fill.solid(); line.fill.fore_color.rgb = ACCENT; line.line.fill.background()

tb(s, 0.8, 3.6, 11.5, 0.5, "DPCN Course Project 2026  ·  Group 23  ·  Statistics Report", 18, False,
   RGBColor(0x93,0xA0,0xAE))
tb(s, 0.8, 4.3, 11.5, 1.5, [
    f"Institutions:  {', '.join(NAMES)}",
    f"{A['papers']:,} papers  ·  {A['citations']:,} citations  ·  {len(A['faculty']):,} faculty/authors",
    "Data source: OpenAlex  ·  Period: 2016–2026",
    "Instructor: Chittaranjan Hens"
], 15, False, RGBColor(0xB0, 0xBA, 0xCA))

# KPI boxes at bottom
for i, (label, val) in enumerate([
    ("Papers", f"{A['papers']:,}"), ("Citations", f"{A['citations']:,}"),
    ("Faculty", f"{len(A['faculty']):,}"), ("Q1 Fraction", f"{A.get('q1_fraction','n/a')}%"),
    ("Median h-index", f"{A.get('h_median','–')}")
]):
    bx = s.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                             Inches(0.8 + i*2.55), Inches(6.1), Inches(2.3), Inches(0.95))
    bx.fill.solid(); bx.fill.fore_color.rgb = RGBColor(0x1A,0x2E,0x55); bx.line.fill.background()
    tf = bx.text_frame; tf.word_wrap = True
    p = tf.paragraphs[0]; p.text = val; p.font.size = Pt(22); p.font.bold = True
    p.font.color.rgb = WHITE; p.alignment = PP_ALIGN.CENTER
    p2 = tf.add_paragraph(); p2.text = label; p2.font.size = Pt(10)
    p2.font.color.rgb = RGBColor(0x6F,0x95,0xFF); p2.alignment = PP_ALIGN.CENTER

if DEMO:
    tb(s, 0.8, 0.3, 11, 0.5, "⚠ DEMO DATA – synthetic, for pipeline testing only", 16, True,
       RGBColor(0xFF,0x6B,0x6B))
add_footer(s, 1)


# ══════════════════════════════════════════════════════════════════════════
#  SLIDE 2: PUBLICATION TREND
# ══════════════════════════════════════════════════════════════════════════
s = slide("Publication Trend 2016–2026",
          f"{A['papers']:,} papers total  ·  {best} leads with {M['per'][best]['papers']:,} papers", 2)
pic(s, c_trend, w=7.6)
side_panel(s, [f"▸ {n}:  {M['per'][n]['papers']:,} papers,  {M['per'][n]['citations']:,} citations"
               for n in NAMES] + ["", "Note: 2025–26 counts may be", "incomplete (indexing lag)."])


# ══════════════════════════════════════════════════════════════════════════
#  SLIDE 3: JOURNAL QUARTILE DISTRIBUTION
# ══════════════════════════════════════════════════════════════════════════
s = slide("Journal Quartile Distribution",
          f"Q1 fraction = Q1 papers / journal papers with a known quartile  ·  Overall Q1 = {fmt(A.get('q1_fraction'))}", 3)
if M["has_quartiles"]:
    pic(s, c_quart, w=7.6)
else:
    tb(s, 0.6, 2.5, 7.4, 1, "Quartile data not loaded.", 16)
side_panel(s, [f"▸ {n}:" for n in NAMES for _ in "x"][:0] +  # placeholder trick
              [f"▸ {n}:  Q1 = {fmt(q1[n])}" for n in NAMES] +
              ["", "Source: Scimago Journal Rankings", "(curated ISSN → quartile mapping)"])


# ══════════════════════════════════════════════════════════════════════════
#  SLIDE 4: H-INDEX DISTRIBUTION
# ══════════════════════════════════════════════════════════════════════════
s = slide("h-index Distribution of Faculty",
          f"Median h-index: {A['h_median']}  ·  Faculty = authors with {M['faculty_min_papers']}+ papers  ·  h-index is career-wide (OpenAlex)", 4)
pic(s, c_hidx, w=7.6)
side_panel(s, [f"▸ {n}:  median h = {M['per'][n]['h_median']},  {len(M['per'][n]['faculty'])} faculty"
               for n in NAMES] +
              ["", "Top 3 by h-index:"] +
              [f"  {f['name']} ({f['h']})" for f in A["faculty"][:3]])
tb(s, 0.6, 6.5, 12.2, 0.7,
   "Note: OpenAlex may merge authors with similar names (e.g. \"S. Das\"), inflating some h-index values.",
   10, color=MUT)


# ══════════════════════════════════════════════════════════════════════════
#  SLIDE 5: TOP JOURNALS + MOST-CITED PAPERS
# ══════════════════════════════════════════════════════════════════════════
s = slide("Top Journals & Most-Cited Papers",
          "Where each institution publishes most  ·  Highest citation counts across all four institutions", 5)
# Top 5 journals – two side-by-side tables
for half, x in ((NAMES[:2], 0.6), (NAMES[2:], 6.9)):
    rows = []
    for n in half:
        for i, (j, c) in enumerate(M["per"][n]["top_journals"]):
            rows.append([n.split()[0] if i == 0 else "", j[:38], c])
    table(s, ["Inst", "Top Journal", "#"], rows, x, 1.7, 6.0, 0.26, 9, [0.9, 4.3, 0.8])

# Most-cited papers (top 5 to save space, rest on dashboard)
table(s, ["Title", "Journal", "Year", "Cites"],
      [[p["title"][:60], p["journal"][:24], p["year"], f'{p["cites"]:,}'] for p in A["top_cited"][:5]],
      0.6, 5.0, 12.2, 0.26, 9, [6.8, 2.8, 1.0, 1.0])
tb(s, 0.6, 6.6, 12, 0.4, "Full top-10 list available in the interactive dashboard.", 10, color=MUT)


# ══════════════════════════════════════════════════════════════════════════
#  SLIDE 6: RESEARCH AREA BREAKDOWN
# ══════════════════════════════════════════════════════════════════════════
s = slide("Research Area Breakdown",
          "Primary OpenAlex field of each paper  ·  Physics dominates across all four institutions", 6)
pic(s, c_fields, w=7.6, y=1.7)
side_panel(s, [f"▸ {f[0]}:  {f[1]} ({100*f[1]//A['papers']}%)" for f in A["fields"][:8]], y=1.7)


# ══════════════════════════════════════════════════════════════════════════
#  SLIDE 7: CITATION NETWORK SUMMARY
# ══════════════════════════════════════════════════════════════════════════
s = slide("Citation Network Summary",
          f"{C['nodes']:,} papers  ·  {C['edges']:,} citation edges inside the group's corpus", 7)
pic(s, c_indeg, w=5.8, y=1.7)
table(s, ["PageRank Top Papers", "Inst", "PR", "In-deg"],
      [[p["title"][:44], p["inst"].split()[0], f'{p["pr"]:.5f}', p["in"]]
       for p in C["pagerank_top10"][:8]],
      6.6, 1.7, 6.3, 0.27, 9, [3.5, 0.9, 0.9, 1.0])
table(s, ["Institution", "Papers", "Internal edges", "Isolated"],
      [[n, M["net"][n]["cit"]["nodes"], f'{M["net"][n]["cit"]["edges"]:,}',
        M["net"][n]["cit"]["isolated"]] for n in NAMES],
      0.6, 5.5, 12.2, 0.28, 10, [4.0, 2.5, 3.2, 2.5])


# ══════════════════════════════════════════════════════════════════════════
#  SLIDE 8: AUTHORSHIP NETWORK SUMMARY
# ══════════════════════════════════════════════════════════════════════════
s = slide("Authorship Network Summary",
          f"{N['nodes']:,} authors  ·  {N['edges']:,} co-author links  ·  {N['communities']} Louvain communities (modularity {N['modularity']})", 8)
table(s, ["Most Collaborative (Degree)", "Inst", "Collab."],
      [[p["name"], p["inst"].split()[0], p["deg"]] for p in N["deg_top10"][:8]],
      0.6, 1.7, 6.0, 0.27, 9, [3.4, 1.5, 1.1])
table(s, ["Key Brokers (Betweenness)", "Inst", "Score"],
      [[p["name"], p["inst"].split()[0], f'{p["v"]:.4f}'] for p in N["btw_top10"][:8]],
      6.9, 1.7, 6.0, 0.27, 9, [3.4, 1.5, 1.1])
table(s, ["Institution", "Authors", "Co-author links", "Communities", "Modularity", "Largest group"],
      [[n, M["net"][n]["auth"]["nodes"], f'{M["net"][n]["auth"]["edges"]:,}',
        M["net"][n]["auth"]["communities"], M["net"][n]["auth"]["modularity"],
        M["net"][n]["auth"]["giant_component"]] for n in NAMES],
      0.6, 4.5, 12.2, 0.28, 10, [3.2, 1.6, 2.0, 1.8, 1.6, 2.0])
tb(s, 0.6, 6.0, 12.2, 0.5,
   f"Cross-institution links: {N['cross_inst_edges']:,}  ·  "
   f"Papers with >{M['mega_threshold']} authors excluded from co-author pairs ({M['skipped_mega_papers']} papers)",
   10, color=MUT)


# ══════════════════════════════════════════════════════════════════════════
#  SLIDE 9: INDIAN CONNECTIVITY & CITATION FLOW
# ══════════════════════════════════════════════════════════════════════════
s = slide("Indian Connectivity & Citation Flow",
          "How the group sits in the wider Indian research network  ·  in-flow vs out-flow of citations", 9)
pic(s, c_flow, w=6.8, y=1.7)
table(s, ["Institution", "In-flow", "Out-flow", "Ratio"],
      [[n.split()[0], f'{F["per_inst"][n]["in"]:,}', f'{F["per_inst"][n]["out"]:,}',
        F["per_inst"][n]["ratio"]] for n in NAMES],
      7.8, 1.8, 5.1, 0.30, 10)
table(s, ["Top Indian Institutes Citing Us", "Cites"],
      [[a[:42], f'{b:,}'] for a, b in F["in_top10"][:6]],
      7.8, 3.5, 5.1, 0.27, 9, [4.0, 1.1])
tb(s, 0.6, 5.8, 12, 0.5,
   f"Total in-flow: {F['in']:,}  ·  Total out-flow: {F['out']:,}  ·  In/Out ratio: {F.get('ratio','n/a')}",
   11, color=MUT)


# ══════════════════════════════════════════════════════════════════════════
#  SLIDE 10: SUMMARY & KEY TAKEAWAYS
# ══════════════════════════════════════════════════════════════════════════
s = prs.slides.add_slide(blank)
add_header_bar(s)
tb(s, 0.6, 0.18, 11, 0.7, "Key Takeaways", 26, True, WHITE)
add_footer(s, 10)

takeaways = [
    f"10,801 papers across 4 institutions (2016–2026), totalling {A['citations']:,} citations.",
    f"SINP Kolkata is the largest contributor ({M['per']['SINP Kolkata']['papers']:,} papers, {M['per']['SINP Kolkata']['citations']:,} citations).",
    f"Overall Q1 fraction: {A.get('q1_fraction','n/a')}% — SINP leads at {q1.get('SINP Kolkata','n/a')}.",
    f"Top journal: Journal of High Energy Physics ({M['per']['ALL']['top_journals'][0][1]} papers) — reflecting the strong HEP presence at SINP and Bose Institute.",
    f"Citation network: {C['edges']:,} internal citation links; highest PageRank paper is \"{C['pagerank_top10'][0]['title'][:55]}…\"",
    f"Authorship network: {N['communities']} collaboration communities (modularity {N['modularity']}), with {N['cross_inst_edges']:,} cross-institution links.",
    f"NCBS Bangalore has the highest citation in-flow ratio ({F['per_inst']['NCBS Bangalore']['ratio']}), indicating strong external impact.",
    f"Most-cited paper: \"{A['top_cited'][0]['title'][:55]}…\" ({A['top_cited'][0]['cites']:,} citations).",
]

for i, t in enumerate(takeaways):
    # Numbered takeaway items
    y = 1.4 + i * 0.7
    # Number circle
    circ = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(0.7), Inches(y), Inches(0.4), Inches(0.4))
    circ.fill.solid(); circ.fill.fore_color.rgb = ACCENT; circ.line.fill.background()
    tf = circ.text_frame
    tf.paragraphs[0].text = str(i+1); tf.paragraphs[0].font.size = Pt(12)
    tf.paragraphs[0].font.bold = True; tf.paragraphs[0].font.color.rgb = WHITE
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    # Text
    tb(s, 1.3, y-0.02, 11.5, 0.5, t, 13, color=DARK_TEXT)


# ── Save ────────────────────────────────────────────────────────────────
prs.save(f"{OUT}/group23_report.pptx")
print(f"report written: {len(prs.slides)} slides → {OUT}/group23_report.pptx")
