# import matplotlib
# matplotlib.use("Agg")
# import matplotlib.pyplot as plt
# import pandas as pd
# from rectpack import newPacker, MaxRectsBssf, PackingMode, SORT_AREA
#
# T = 18  # thickness of main board (mm)
# B18, B6 = "18mm board", "6mm back panel"
#
# # ---------- 1. PROJECT TEMPLATES: what you want to build -> list of parts ----------
# # part = (name, length, width, qty, material)
# def bookshelf(W, H, D, shelves, doors):
#     return [
#         ("Side panel", H, D, 2, B18),
#         ("Top / Bottom", W - 2 * T, D, 2, B18),
#         ("Shelf", W - 2 * T, D - 20, shelves, B18),
#         back_panels(W, H),
#     ]
#
# def wardrobe(W, H, D, shelves, doors):
#     doors = max(doors, 1)
#     return [
#         ("Side panel", H, D, 2, B18),
#         ("Top / Bottom", W - 2 * T, D, 2, B18),
#         ("Shelf", W - 2 * T, D - 20, shelves, B18),
#         ("Door", H - 4, round(W / doors) - 4, doors, B18),
#         back_panels(W, H),
#     ]
#
# def desk(W, H, D, shelves, doors):
#     return [
#         ("Table top", W, D, 1, B18),
#         ("Side leg panel", H - T, D - 40, 2, B18),
#         ("Modesty panel", W - 2 * T - 100, 300, 1, B18),
#     ] + ([("Drawer-unit shelf", 400, D - 100, shelves, B18)] if shelves else [])
#
# TEMPLATES = {
#     "Bookshelf": (bookshelf, (800, 1800, 300, 4, 0)),
#     "Wardrobe": (wardrobe, (1800, 2100, 550, 2, 2)),
#     "Study desk": (desk, (1200, 750, 600, 0, 0)),
# }
#
# def back_panels(W, H):
#     """Back panels wider than a sheet are split into equal strips."""
#     n = -(-(W - 4) // 1200)  # ceil
#     return ("Back panel", H - 4, round((W - 4) / n), int(n), B6)
#
# def expand(parts):
#     """Turn (name, l, w, qty, material) rows into one entry per physical piece."""
#     return [(n, l, w, m) for n, l, w, q, m in parts for _ in range(int(q))]
#
# # ---------- 2. NORMAL PLAN: how a worker cuts by hand (in order, no rotation) ----------
# def normal_plan(pieces, SW, SH, kerf):
#     sheets, x, y, row_h = [[]], 0, 0, 0
#     for name, l, w in pieces:
#         pw, ph = l + kerf, w + kerf
#         if pw > SW or ph > SH:           # only turn it if it doesn't fit the sheet
#             pw, ph = ph, pw
#         if x + pw > SW:                  # new row
#             x, y, row_h = 0, y + row_h, 0
#         if y + ph > SH:                  # new sheet
#             sheets.append([]); x = y = row_h = 0
#         sheets[-1].append((x, y, pw - kerf, ph - kerf, name))
#         x += pw; row_h = max(row_h, ph)
#     return sheets
#
# # ---------- 3. OPTIMIZED PLAN: MaxRects packing, biggest first ----------
# def optimized_plan(pieces, SW, SH, kerf, rotate):
#     p = newPacker(mode=PackingMode.Offline, pack_algo=MaxRectsBssf,
#                   sort_algo=SORT_AREA, rotation=rotate)
#     for i, (name, l, w) in enumerate(pieces):
#         p.add_rect(l + kerf, w + kerf, rid=i)
#     p.add_bin(SW, SH, count=float("inf"))
#     p.pack()
#     sheets = {}
#     for b, x, y, w, h, rid in p.rect_list():
#         sheets.setdefault(b, []).append((x, y, w - kerf, h - kerf, pieces[rid][0]))
#     return [sheets[k] for k in sorted(sheets)]
#
# # ---------- 3b. LEFTOVER REUSE: find offcuts and suggest products ----------
# # idea = (name, material, [(length, width), ...] pieces for ONE unit)
# IDEAS = [
#     ("Coaster set (4 pcs)", B18, [(100, 100)] * 4),
#     ("Chopping / serving board", B18, [(400, 250)]),
#     ("Book stand", B18, [(300, 200), (300, 150)]),
#     ("Wall shelf with brackets", B18, [(600, 200), (150, 150), (150, 150)]),
#     ("Small toolbox / storage box", B18, [(300, 200), (300, 150), (300, 150), (200, 150), (200, 150)]),
#     ("Plant stand", B18, [(300, 300), (400, 100), (400, 100), (400, 100), (400, 100)]),
#     ("Kids' stool", B18, [(300, 300), (300, 250), (300, 250), (250, 200)]),
#     ("Shoe rack tier", B18, [(700, 250), (250, 150), (250, 150)]),
#     ("Drawer divider set", B18, [(350, 80)] * 4),
#     ("Picture-frame backing / notice board", B6, [(400, 300)]),
#     ("Drawer bottom panels (x2)", B6, [(400, 300)] * 2),
#     ("Organizer tray base", B6, [(300, 200)]),
# ]
#
# def free_rects(sheet, SW, SH, kerf, min_side=100, max_n=12):
#     """Largest empty rectangles left on a sheet (greedy), as (x, y, w, h)."""
#     foot = [(x, y, min(SW, x + w + kerf), min(SH, y + h + kerf)) for x, y, w, h, _ in sheet]
#     xs = sorted({0, SW} | {f[0] for f in foot} | {f[2] for f in foot})
#     ys = sorted({0, SH} | {f[1] for f in foot} | {f[3] for f in foot})
#     nx, ny = len(xs) - 1, len(ys) - 1
#     occ = [[any(xs[i] >= fx and xs[i + 1] <= fx2 and ys[j] >= fy and ys[j + 1] <= fy2
#                 for fx, fy, fx2, fy2 in foot) for i in range(nx)] for j in range(ny)]
#     out = []
#     for _ in range(max_n):
#         best, box = 0, None
#         for r1 in range(ny):
#             free = [True] * nx
#             for r2 in range(r1, ny):
#                 free = [free[i] and not occ[r2][i] for i in range(nx)]
#                 hgt, i = ys[r2 + 1] - ys[r1], 0
#                 while i < nx:
#                     if free[i]:
#                         j = i
#                         while j < nx and free[j]:
#                             j += 1
#                         if (xs[j] - xs[i]) * hgt > best:
#                             best, box = (xs[j] - xs[i]) * hgt, (i, j, r1, r2)
#                         i = j
#                     else:
#                         i += 1
#         if box is None:
#             break
#         i, j, r1, r2 = box
#         for r in range(r1, r2 + 1):
#             for c in range(i, j):
#                 occ[r][c] = True
#         w, h = xs[j] - xs[i], ys[r2 + 1] - ys[r1]
#         if min(w, h) >= min_side:
#             out.append((xs[i], ys[r1], w, h))
#     return out
#
# def units_possible(parts, pool, kerf, rotate, cap=12):
#     """How many units of an idea fit into the leftover rectangles."""
#     best = 0
#     for n in range(1, cap + 1):
#         p = newPacker(mode=PackingMode.Offline, pack_algo=MaxRectsBssf,
#                       sort_algo=SORT_AREA, rotation=rotate)
#         k = 0
#         for l, w in parts:
#             for _ in range(n):
#                 p.add_rect(l + kerf, w + kerf, rid=k); k += 1
#         for _, _, w, h in pool:
#             p.add_bin(w, h)
#         p.pack()
#         if len(p.rect_list()) < k:
#             break
#         best = n
#     return best
#
# def stats(sheets, SW, SH):
#     used = sum(w * h for s in sheets for _, _, w, h, _ in s)
#     total = len(sheets) * SW * SH
#     return len(sheets), (100 * (1 - used / total) if total else 0.0)
#
# def draw(sheets, SW, SH, title, left=None):
#     import streamlit as st
#     st.markdown(f"**{title}**")
#     cols = st.columns(2)
#     for i, s in enumerate(sheets):
#         fig, ax = plt.subplots(figsize=(5, 2.6))
#         ax.set_xlim(0, SW); ax.set_ylim(0, SH); ax.set_aspect("equal"); ax.axis("off")
#         ax.add_patch(plt.Rectangle((0, 0), SW, SH, fc="#f1f1f1", ec="k"))
#         for x, y, w, h, name in s:
#             ax.add_patch(plt.Rectangle((x, y), w, h, fc="#8ecae6", ec="k"))
#             if w > 250 and h > 120:
#                 ax.text(x + w / 2, y + h / 2, f"{name}\n{int(w)}x{int(h)}",
#                         ha="center", va="center", fontsize=5)
#         for x, y, w, h in (left[i] if left else []):
#             ax.add_patch(plt.Rectangle((x, y), w, h, fc="#ffd6a5", ec="#e07a00", hatch="//"))
#             ax.text(x + w / 2, y + h / 2, f"{int(w)}x{int(h)}", ha="center",
#                     va="center", fontsize=5, color="#7a3e00")
#         ax.set_title(f"Sheet {i + 1}", fontsize=8)
#         cols[i % 2].pyplot(fig); plt.close(fig)
#
# # ---------- 4. USER INTERFACE ----------
# def main():
#     import streamlit as st
#     st.set_page_config(page_title="Waste Reducer", layout="wide")
#     st.title("Smart Raw Material Waste Reducer")
#
#     with st.sidebar:
#         st.header("1. What do you want to build?")
#         project = st.selectbox("Project", list(TEMPLATES) + ["Custom parts list"])
#         new_parts = []
#         if project != "Custom parts list":
#             fn, (dW, dH, dD, dS, dDr) = TEMPLATES[project]
#             W = st.number_input("Width (mm)", 300, 4000, dW, key=f"{project}_W")
#             H = st.number_input("Height (mm)", 300, 3000, dH, key=f"{project}_H")
#             D = st.number_input("Depth (mm)", 200, 1500, dD, key=f"{project}_D")
#             shelves = st.number_input("Shelves", 0, 12, dS, key=f"{project}_S")
#             doors = st.number_input("Doors", 0, 6, dDr, key=f"{project}_Dr")
#             qty = st.number_input("How many units?", 1, 50, 1, key=f"{project}_Q")
#             new_parts = [(f"{project} - {n}", l, w, q * qty, m)
#                          for n, l, w, q, m in fn(W, H, D, shelves, doors)]
#         else:
#             st.caption("Type your own parts in the table on the main page.")
#         c1, c2 = st.columns(2)
#         add = c1.button("Add to job", type="primary")
#         clear = c2.button("Clear job")
#         st.header("2. Material")
#         SW = st.number_input("Sheet length (mm)", 500, 6000, 2440)
#         SH = st.number_input("Sheet width (mm)", 500, 3000, 1220)
#         kerf = st.number_input("Blade thickness (mm)", 0, 10, 3)
#         price = {B18: st.number_input("Price per 18mm sheet", 0, 1000000, 8500),
#                  B6: st.number_input("Price per 6mm sheet", 0, 1000000, 3000)}
#         rotate = st.checkbox("Allow rotating pieces (off for wood grain)", True)
#
#     if "job" not in st.session_state:
#         st.session_state.job = []
#     if project == "Custom parts list":
#         st.write("Custom parts: name, length, width, qty, material (18mm board or 6mm back panel).")
#         df = st.data_editor(pd.DataFrame(
#             [("Panel A", 800, 600, 4, B18), ("Panel B", 500, 400, 6, B18)],
#             columns=["name", "length", "width", "qty", "material"]), num_rows="dynamic")
#         new_parts = [tuple(r) for r in df.itertuples(index=False)]
#     if clear:
#         st.session_state.job = []
#     if add:
#         st.session_state.job += new_parts
#     parts = st.session_state.job
#
#     if not parts:
#         st.info("Pick a project in the sidebar, set its size, and click 'Add to job'. "
#                 "Add several items to see the biggest savings.")
#         return
#
#     st.subheader("Parts list (generated automatically)")
#     st.dataframe(pd.DataFrame(parts, columns=["Part", "Length", "Width", "Qty", "Material"]),
#                  hide_index=True)
#
#     if not st.button("Calculate cutting plan", type="primary"):
#         return
#
#     items = expand(parts)
#     for n, l, w, m in items:
#         if min(l, w) > min(SW, SH) or max(l, w) > max(SW, SH):
#             st.error(f"'{n}' ({l}x{w}) is bigger than the sheet."); return
#
#     tot_n = tot_o = 0
#     for mat in dict.fromkeys(m for *_, m in items):
#         pcs = [(n, l, w) for n, l, w, m in items if m == mat]
#         a, b = normal_plan(pcs, SW, SH, kerf), optimized_plan(pcs, SW, SH, kerf, rotate)
#         na, wa = stats(a, SW, SH); nb, wb = stats(b, SW, SH)
#         pr = price.get(mat, 0); tot_n += na * pr; tot_o += nb * pr
#         st.header(mat)
#         c1, c2, c3 = st.columns(3)
#         c1.metric("Normal plan", f"{na} sheets", f"{wa:.1f}% waste", delta_color="off")
#         c2.metric("Optimized plan", f"{nb} sheets", f"{wb:.1f}% waste", delta_color="off")
#         c3.metric("Saved", f"{na - nb} sheets", f"{(na - nb) * pr:,} money")
#         left = [free_rects(sh, SW, SH, kerf) for sh in b]
#         draw(a, SW, SH, "Normal plan"); draw(b, SW, SH, "Optimized plan (orange = reusable leftovers)", left)
#         pool = [(i, *r) for i, rs in enumerate(left) for r in rs]
#         st.subheader(f"Leftover {mat}: what else can you make?")
#         if not pool:
#             st.write("No usable leftovers (all offcuts are smaller than 100 mm).")
#         else:
#             st.dataframe(pd.DataFrame([(f"Sheet {i + 1}", w, h) for i, _, _, w, h in pool],
#                          columns=["Offcut on", "Length", "Width"]), hide_index=True)
#             rows = []
#             for name, imat, parts in IDEAS:
#                 if imat != mat:
#                     continue
#                 n = units_possible(parts, [(0, 0, w, h) for _, _, _, w, h in pool], kerf, rotate)
#                 if n:
#                     need = ", ".join(f"{parts.count(q)} x {q[0]}x{q[1]}" for q in dict.fromkeys(parts))
#                     rows.append((name, "12+" if n >= 12 else str(n), need))
#             if rows:
#                 st.success("Ideas you can make from this leftover material:")
#                 st.dataframe(pd.DataFrame(rows, columns=["Product idea", "Units possible", "Pieces needed (mm)"]),
#                              hide_index=True)
#             else:
#                 st.write("Leftovers are too small for the products in the idea list.")
#     st.success(f"Total cost - normal: {tot_n:,} | optimized: {tot_o:,} | "
#                f"estimated saving: {tot_n - tot_o:,}")
#
# if __name__ == "__main__":
#     main()









"""Smart Raw Material Waste Reducer - project-based prototype.
Run:  streamlit run app.py
"""
import json, os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from rectpack import newPacker, MaxRectsBssf, PackingMode, SORT_AREA

T = 18  # thickness of main board (mm)
B18, B6 = "18mm board", "6mm back panel"

# ---------- 1. PROJECT TEMPLATES: what you want to build -> list of parts ----------
# part = (name, length, width, qty, material)
def bookshelf(W, H, D, shelves, doors):
    return [
        ("Side panel", H, D, 2, B18),
        ("Top / Bottom", W - 2 * T, D, 2, B18),
        ("Shelf", W - 2 * T, D - 20, shelves, B18),
        back_panels(W, H),
    ]

def wardrobe(W, H, D, shelves, doors):
    doors = max(doors, 1)
    return [
        ("Side panel", H, D, 2, B18),
        ("Top / Bottom", W - 2 * T, D, 2, B18),
        ("Shelf", W - 2 * T, D - 20, shelves, B18),
        ("Door", H - 4, round(W / doors) - 4, doors, B18),
        back_panels(W, H),
    ]

def desk(W, H, D, shelves, doors):
    return [
        ("Table top", W, D, 1, B18),
        ("Side leg panel", H - T, D - 40, 2, B18),
        ("Modesty panel", W - 2 * T - 100, 300, 1, B18),
    ] + ([("Drawer-unit shelf", 400, D - 100, shelves, B18)] if shelves else [])

TEMPLATES = {
    "Bookshelf": (bookshelf, (800, 1800, 300, 4, 0)),
    "Wardrobe": (wardrobe, (1800, 2100, 550, 2, 2)),
    "Study desk": (desk, (1200, 750, 600, 0, 0)),
}

def back_panels(W, H):
    """Back panels wider than a sheet are split into equal strips."""
    n = -(-(W - 4) // 1200)  # ceil
    return ("Back panel", H - 4, round((W - 4) / n), int(n), B6)

def expand(parts):
    """Turn (name, l, w, qty, material) rows into one entry per physical piece."""
    return [(n, l, w, m) for n, l, w, q, m in parts for _ in range(int(q))]

# ---------- 2. NORMAL PLAN: how a worker cuts by hand (in order, no rotation) ----------
def normal_plan(pieces, SW, SH, kerf):
    sheets, x, y, row_h = [[]], 0, 0, 0
    for name, l, w in pieces:
        pw, ph = l + kerf, w + kerf
        if pw > SW or ph > SH:           # only turn it if it doesn't fit the sheet
            pw, ph = ph, pw
        if x + pw > SW:                  # new row
            x, y, row_h = 0, y + row_h, 0
        if y + ph > SH:                  # new sheet
            sheets.append([]); x = y = row_h = 0
        sheets[-1].append((x, y, pw - kerf, ph - kerf, name))
        x += pw; row_h = max(row_h, ph)
    return sheets

# ---------- 3. OPTIMIZED PLAN: MaxRects packing, biggest first ----------
def optimized_plan(pieces, SW, SH, kerf, rotate):
    p = newPacker(mode=PackingMode.Offline, pack_algo=MaxRectsBssf,
                  sort_algo=SORT_AREA, rotation=rotate)
    for i, (name, l, w) in enumerate(pieces):
        p.add_rect(l + kerf, w + kerf, rid=i)
    p.add_bin(SW, SH, count=float("inf"))
    p.pack()
    sheets = {}
    for b, x, y, w, h, rid in p.rect_list():
        sheets.setdefault(b, []).append((x, y, w - kerf, h - kerf, pieces[rid][0]))
    return [sheets[k] for k in sorted(sheets)]

# ---------- 3a. STOCK-FIRST PLAN: fill inventory offcuts, then open new sheets ----------
# A "bin" is one physical board the parts are cut from:
#   dict(w, h, src, parts)  src = inventory row index (reused stock) or None (new sheet)
def as_bins(sheets, SW, SH):
    """Wrap plain sheet lists (normal / optimized plan) as new-sheet bins."""
    return [dict(w=SW, h=SH, src=None, parts=s) for s in sheets]

def stock_pieces(inv, mat, kinds):
    """One (length, width, inv_index) per physical stock piece, smallest first,
    so small scraps get used up and big offcuts stay available for big parts."""
    out = []
    for idx, r in enumerate(inv):
        try:
            L, W, q = int(r["length"]), int(r["width"]), int(r.get("qty", 1))
        except (KeyError, TypeError, ValueError):
            continue
        if r.get("material") == mat and r.get("kind") in kinds and L > 0 and W > 0:
            out += [(L, W, idx)] * min(q, 50)
    return sorted(out, key=lambda s: s[0] * s[1])

def pack_into(pieces, ids, stock, kerf, rotate, sheet=None):
    """Pack pieces[ids] into the stock boards (in order) and, if `sheet` is given,
    into unlimited new sheets after that. Returns (bins, ids that did not fit)."""
    p = newPacker(mode=PackingMode.Offline, pack_algo=MaxRectsBssf,
                  sort_algo=SORT_AREA, rotation=rotate)
    for i in ids:
        p.add_rect(pieces[i][1] + kerf, pieces[i][2] + kerf, rid=i)
    for k, (L, W, _) in enumerate(stock):          # rectpack opens bins in this order
        p.add_bin(L, W, bid=k)
    if sheet:
        p.add_bin(*sheet, count=float("inf"), bid=None)
    p.pack()
    bins, placed = [], set()
    for b in p:
        if len(b):
            bins.append(dict(w=b.width, h=b.height,
                             src=None if b.bid is None else stock[b.bid][2],
                             parts=[(r.x, r.y, r.width - kerf, r.height - kerf, pieces[r.rid][0])
                                    for r in b]))
            placed.update(r.rid for r in b)
    return bins, [i for i in ids if i not in placed]

def stock_first_plan(pieces, stock, SW, SH, kerf, rotate):
    """Try two strategies and keep the one needing the fewest new sheets:
    A) fill stock first, then pack whatever is left onto new sheets;
    B) pack everything in one pass with stock boards offered before new sheets."""
    ids = list(range(len(pieces)))
    on_stock, rest = pack_into(pieces, ids, stock, kerf, rotate)
    two_phase = on_stock + pack_into(pieces, rest, [], kerf, rotate, (SW, SH))[0]
    one_pass = pack_into(pieces, ids, stock, kerf, rotate, (SW, SH))[0]
    score = lambda bins: (sum(b["src"] is None for b in bins), len(bins))
    best = min(two_phase, one_pass, key=score)
    return sorted(best, key=lambda b: b["src"] is None)   # reused stock first, then new sheets

def bin_names(bins, inv):
    """Display names: 'Stock 1 - <label>' for reused boards, 'New sheet 1' for bought ones."""
    names, ns, nn = [], 0, 0
    for b in bins:
        if b["src"] is None:
            nn += 1; names.append(f"New sheet {nn}")
        else:
            ns += 1
            label = inv[b["src"]].get("label") or inv[b["src"]].get("kind", "stock")
            names.append(f"Stock {ns} - {label}")
    return names

# ---------- 3b. LEFTOVER REUSE: find offcuts and suggest products ----------
# idea = (name, material, [(length, width), ...] pieces for ONE unit)
IDEAS = [
    ("Coaster set (4 pcs)", B18, [(100, 100)] * 4),
    ("Chopping / serving board", B18, [(400, 250)]),
    ("Book stand", B18, [(300, 200), (300, 150)]),
    ("Wall shelf with brackets", B18, [(600, 200), (150, 150), (150, 150)]),
    ("Small toolbox / storage box", B18, [(300, 200), (300, 150), (300, 150), (200, 150), (200, 150)]),
    ("Plant stand", B18, [(300, 300), (400, 100), (400, 100), (400, 100), (400, 100)]),
    ("Kids' stool", B18, [(300, 300), (300, 250), (300, 250), (250, 200)]),
    ("Shoe rack tier", B18, [(700, 250), (250, 150), (250, 150)]),
    ("Drawer divider set", B18, [(350, 80)] * 4),
    ("Picture-frame backing / notice board", B6, [(400, 300)]),
    ("Drawer bottom panels (x2)", B6, [(400, 300)] * 2),
    ("Organizer tray base", B6, [(300, 200)]),
]

def free_rects(sheet, SW, SH, kerf, min_side=100, max_n=12):
    """Largest empty rectangles left on a sheet (greedy), as (x, y, w, h)."""
    foot = [(x, y, min(SW, x + w + kerf), min(SH, y + h + kerf)) for x, y, w, h, _ in sheet]
    xs = sorted({0, SW} | {f[0] for f in foot} | {f[2] for f in foot})
    ys = sorted({0, SH} | {f[1] for f in foot} | {f[3] for f in foot})
    nx, ny = len(xs) - 1, len(ys) - 1
    occ = [[any(xs[i] >= fx and xs[i + 1] <= fx2 and ys[j] >= fy and ys[j + 1] <= fy2
                for fx, fy, fx2, fy2 in foot) for i in range(nx)] for j in range(ny)]
    out = []
    for _ in range(max_n):
        best, box = 0, None
        for r1 in range(ny):
            free = [True] * nx
            for r2 in range(r1, ny):
                free = [free[i] and not occ[r2][i] for i in range(nx)]
                hgt, i = ys[r2 + 1] - ys[r1], 0
                while i < nx:
                    if free[i]:
                        j = i
                        while j < nx and free[j]:
                            j += 1
                        if (xs[j] - xs[i]) * hgt > best:
                            best, box = (xs[j] - xs[i]) * hgt, (i, j, r1, r2)
                        i = j
                    else:
                        i += 1
        if box is None:
            break
        i, j, r1, r2 = box
        for r in range(r1, r2 + 1):
            for c in range(i, j):
                occ[r][c] = True
        w, h = xs[j] - xs[i], ys[r2 + 1] - ys[r1]
        if min(w, h) >= min_side:
            out.append((xs[i], ys[r1], w, h))
    return out

def units_possible(parts, pool, kerf, rotate, cap=12):
    """How many units of an idea fit into the leftover rectangles."""
    best = 0
    for n in range(1, cap + 1):
        p = newPacker(mode=PackingMode.Offline, pack_algo=MaxRectsBssf,
                      sort_algo=SORT_AREA, rotation=rotate)
        k = 0
        for l, w in parts:
            for _ in range(n):
                p.add_rect(l + kerf, w + kerf, rid=k); k += 1
        for _, _, w, h in pool:
            p.add_bin(w, h)
        p.pack()
        if len(p.rect_list()) < k:
            break
        best = n
    return best

# ---------- 3c. INVENTORY (saved to inventory.json next to app.py) ----------
INV_FILE = Path(os.environ.get("INVENTORY_FILE", Path(__file__).with_name("inventory.json")))
KINDS = ["Full sheet", "Offcut"]

def inv_load():
    try:
        return json.loads(INV_FILE.read_text())
    except Exception:
        return []

def inv_save(rows):
    INV_FILE.write_text(json.dumps(rows, indent=1))

def inv_add(new_rows):
    inv_save(inv_load() + new_rows)

def inv_clean(df):
    """Turn the edited table back into valid inventory rows (drops incomplete rows)."""
    def val(x, default):
        return default if pd.isna(x) or x in ("", None) else x
    rows = []
    for r in df.to_dict("records"):
        try:
            L, W = int(r["length"]), int(r["width"])
        except (TypeError, ValueError):
            continue
        if L > 0 and W > 0:
            rows.append(dict(label=str(val(r.get("label"), "")), material=val(r.get("material"), B18),
                             kind=val(r.get("kind"), KINDS[0]), length=max(L, W), width=min(L, W),
                             qty=max(int(val(r.get("qty"), 1)), 1)))
    return rows

def show_ideas(mat, rects, kerf, rotate, cap=12):
    """Show which products fit into the given rectangles [(x, y, w, h), ...]."""
    import streamlit as st
    rows = []
    for name, imat, parts in IDEAS:
        if imat != mat:
            continue
        n = units_possible(parts, rects, kerf, rotate, cap)
        if n:
            need = ", ".join(f"{parts.count(q)} x {q[0]}x{q[1]}" for q in dict.fromkeys(parts))
            rows.append((name, f"{cap}+" if n >= cap else str(n), need))
    if rows:
        st.success("Ideas you can make from this material:")
        st.dataframe(pd.DataFrame(rows, columns=["Product idea", "Units possible", "Pieces needed (mm)"]),
                     hide_index=True)
    else:
        st.write("These pieces are too small for the products in the idea list.")

def stats(bins):
    """(new sheets bought, waste % over every board that was cut)."""
    used = sum(w * h for b in bins for _, _, w, h, _ in b["parts"])
    total = sum(b["w"] * b["h"] for b in bins)
    return sum(b["src"] is None for b in bins), (100 * (1 - used / total) if total else 0.0)

def draw(bins, SW, SH, title, left=None, names=None):
    """Draw every board at the same scale as a full sheet. Reused stock boards are
    green with a dashed full-sheet outline, so you can see how small the scrap was."""
    import streamlit as st
    st.markdown(f"**{title}**")
    cols = st.columns(2)
    for i, b in enumerate(bins):
        reused = b["src"] is not None
        fig, ax = plt.subplots(figsize=(5, 2.6))
        ax.set_xlim(0, max(SW, b["w"])); ax.set_ylim(0, max(SH, b["h"]))
        ax.set_aspect("equal"); ax.axis("off")
        if reused:
            ax.add_patch(plt.Rectangle((0, 0), SW, SH, fill=False, ec="#bbbbbb", ls="--"))
            ax.add_patch(plt.Rectangle((0, 0), b["w"], b["h"], fc="#e9f5db", ec="#2d6a4f", lw=2))
        else:
            ax.add_patch(plt.Rectangle((0, 0), b["w"], b["h"], fc="#f1f1f1", ec="k"))
        for x, y, w, h, name in b["parts"]:
            ax.add_patch(plt.Rectangle((x, y), w, h, fc="#95d5b2" if reused else "#8ecae6", ec="k"))
            if w > 250 and h > 120:
                ax.text(x + w / 2, y + h / 2, f"{name}\n{int(w)}x{int(h)}",
                        ha="center", va="center", fontsize=5)
        for x, y, w, h in (left[i] if left else []):
            ax.add_patch(plt.Rectangle((x, y), w, h, fc="#ffd6a5", ec="#e07a00", hatch="//"))
            ax.text(x + w / 2, y + h / 2, f"{int(w)}x{int(h)}", ha="center",
                    va="center", fontsize=5, color="#7a3e00")
        name = names[i] if names else f"Sheet {i + 1}"
        if reused:
            name = f"REUSED {name} ({b['w']}x{b['h']})"
        ax.set_title(name, fontsize=8, color="#2d6a4f" if reused else "k",
                     fontweight="bold" if reused else "normal")
        cols[i % 2].pyplot(fig); plt.close(fig)

# ---------- 4. USER INTERFACE ----------
def planner_page():
    import streamlit as st
    with st.sidebar:
        st.header("1. What do you want to build?")
        project = st.selectbox("Project", list(TEMPLATES) + ["Custom parts list"])
        new_parts = []
        if project != "Custom parts list":
            fn, (dW, dH, dD, dS, dDr) = TEMPLATES[project]
            W = st.number_input("Width (mm)", 300, 4000, dW, key=f"{project}_W")
            H = st.number_input("Height (mm)", 300, 3000, dH, key=f"{project}_H")
            D = st.number_input("Depth (mm)", 200, 1500, dD, key=f"{project}_D")
            shelves = st.number_input("Shelves", 0, 12, dS, key=f"{project}_S")
            doors = st.number_input("Doors", 0, 6, dDr, key=f"{project}_Dr")
            qty = st.number_input("How many units?", 1, 50, 1, key=f"{project}_Q")
            new_parts = [(f"{project} - {n}", l, w, q * qty, m)
                         for n, l, w, q, m in fn(W, H, D, shelves, doors)]
        else:
            st.caption("Type your own parts in the table on the main page.")
        c1, c2 = st.columns(2)
        add = c1.button("Add to job", type="primary")
        clear = c2.button("Clear job")
        st.header("2. Material")
        SW = st.number_input("Sheet length (mm)", 500, 6000, 2440)
        SH = st.number_input("Sheet width (mm)", 500, 3000, 1220)
        kerf = st.number_input("Blade thickness (mm)", 0, 10, 3)
        price = {B18: st.number_input("Price per 18mm sheet", 0, 1000000, 8500),
                 B6: st.number_input("Price per 6mm sheet", 0, 1000000, 3000)}
        rotate = st.checkbox("Allow rotating pieces (off for wood grain)", True)
        st.header("3. Use my stock first")
        inv = inv_load()
        n_off = sum(int(r.get("qty", 1)) for r in inv if r.get("kind") == "Offcut")
        n_full = sum(int(r.get("qty", 1)) for r in inv if r.get("kind") == "Full sheet")
        use_off = st.checkbox(f"Use saved offcuts first ({n_off} in inventory)", n_off > 0,
                              disabled=not n_off)
        use_full = st.checkbox(f"Also use full sheets in inventory ({n_full})", False,
                               disabled=not n_full)
        kinds = {k for k, on in (("Offcut", use_off), ("Full sheet", use_full)) if on}
        st.caption("Parts are cut from your stock before any new sheet is bought. "
                   "Stock you already own counts as free.")

    if "job" not in st.session_state:
        st.session_state.job = []
    if msg := st.session_state.pop("inv_msg", None):
        st.success(msg)
    if project == "Custom parts list":
        st.write("Custom parts: name, length, width, qty, material (18mm board or 6mm back panel).")
        df = st.data_editor(pd.DataFrame(
            [("Panel A", 800, 600, 4, B18), ("Panel B", 500, 400, 6, B18)],
            columns=["name", "length", "width", "qty", "material"]), num_rows="dynamic")
        new_parts = [tuple(r) for r in df.itertuples(index=False)]
    if clear:
        st.session_state.job = []; st.session_state.calc = False
    if add:
        st.session_state.job += new_parts; st.session_state.calc = False
    parts = st.session_state.job

    if not parts:
        st.info("Pick a project in the sidebar, set its size, and click 'Add to job'. "
                "Add several items to see the biggest savings.")
        return

    st.subheader("Parts list (generated automatically)")
    st.dataframe(pd.DataFrame(parts, columns=["Part", "Length", "Width", "Qty", "Material"]),
                 hide_index=True)

    if st.button("Calculate cutting plan", type="primary"):
        st.session_state.calc = True
    if not st.session_state.get("calc"):
        return

    items = expand(parts)
    for n, l, w, m in items:
        if min(l, w) > min(SW, SH) or max(l, w) > max(SW, SH):
            st.error(f"'{n}' ({l}x{w}) is bigger than the sheet."); return

    tot_n = tot_o = tot_stock = 0
    job_used, job_left = [], []      # inventory rows consumed / new offcuts, for "Finish job"
    for mat in dict.fromkeys(m for *_, m in items):
        pcs = [(n, l, w) for n, l, w, m in items if m == mat]
        a = as_bins(normal_plan(pcs, SW, SH, kerf), SW, SH)
        b = as_bins(optimized_plan(pcs, SW, SH, kerf, rotate), SW, SH)
        na, wa = stats(a); nb, wb = stats(b)
        stock = stock_pieces(inv, mat, kinds) if kinds else []
        plan = b
        if stock:
            sp = stock_first_plan(pcs, stock, SW, SH, kerf, rotate)
            if stats(sp)[0] <= nb:          # never let stock reuse cost an extra sheet
                plan = sp
        ns, ws = stats(plan)
        reused = [bn for bn in plan if bn["src"] is not None]
        pr = price.get(mat, 0)
        tot_n += na * pr; tot_o += ns * pr; tot_stock += (nb - ns) * pr

        st.header(mat)
        cols = st.columns(4 if stock else 3)
        cols[0].metric("Normal plan", f"{na} sheets", f"{wa:.1f}% waste", delta_color="off")
        cols[1].metric("Optimized plan", f"{nb} sheets", f"{wb:.1f}% waste", delta_color="off")
        if stock:
            cols[2].metric("Optimized + my stock", f"{ns} new sheets",
                           f"{len(reused)} stock piece(s) reused", delta_color="off")
        cols[-1].metric("Saved", f"{na - ns} sheets", f"{(na - ns) * pr:,} money")

        names = bin_names(plan, inv)
        if reused:
            n_parts = sum(len(bn["parts"]) for bn in reused)
            extra = (f" That saved {nb - ns} new sheet(s) ({(nb - ns) * pr:,} money) "
                     f"compared with the optimized plan alone." if nb > ns else "")
            st.success(f"Reused {len(reused)} piece(s) from your inventory to cut "
                       f"{n_parts} of {len(pcs)} parts.{extra}")
            st.dataframe(pd.DataFrame(
                [(nm, f"{bn['w']}x{bn['h']}", len(bn["parts"]),
                  f"{100 * sum(w * h for _, _, w, h, _ in bn['parts']) / (bn['w'] * bn['h']):.0f}%",
                  ", ".join(dict.fromkeys(p[4] for p in bn["parts"])))
                 for nm, bn in zip(names, plan) if bn["src"] is not None],
                columns=["Reused stock", "Size (mm)", "Parts cut", "Area used", "Parts"]),
                hide_index=True)
        elif stock:
            st.info(f"None of your {len(stock)} {mat} stock piece(s) fit these parts, "
                    "so only new sheets are used.")

        left = [free_rects(bn["parts"], bn["w"], bn["h"], kerf) for bn in plan]
        draw(a, SW, SH, "Normal plan")
        draw(plan, SW, SH, "Optimized plan (green = cut from reused stock, "
             "orange = reusable leftovers)", left, names)
        pool = [(i, *r) for i, rs in enumerate(left) for r in rs]
        job_used += [bn["src"] for bn in reused]
        for i, _, _, w, h in pool:
            src = plan[i]["src"]
            label = (f"Leftover of {inv[src].get('label') or 'stock'}" if src is not None
                     else f"Job offcut ({names[i].lower()})")
            job_left.append(dict(label=label, material=mat, kind="Offcut",
                                 length=int(max(w, h)), width=int(min(w, h)), qty=1))
        st.subheader(f"Leftover {mat}: what else can you make?")
        if not pool:
            st.write("No usable leftovers (all offcuts are smaller than 100 mm).")
        else:
            st.dataframe(pd.DataFrame([(names[i], w, h) for i, _, _, w, h in pool],
                         columns=["Offcut on", "Length", "Width"]), hide_index=True)
            show_ideas(mat, [(0, 0, w, h) for _, _, _, w, h in pool], kerf, rotate)

    st.success(f"Total cost - normal: {tot_n:,} | optimized: {tot_o:,} | "
               f"estimated saving: {tot_n - tot_o:,}"
               + (f" (of which {tot_stock:,} from reusing your stock)" if tot_stock else ""))

    if job_used or job_left:
        st.subheader("Finish job")
        st.caption("When you have cut this job, update the inventory: the stock pieces used "
                   "are removed and every new leftover is saved for the next job.")
        if st.button(f"Finish job: use {len(job_used)} stock piece(s), "
                     f"save {len(job_left)} leftover(s)", type="primary"):
            new_inv = [dict(r) for r in inv]          # the same inventory this plan was built on
            for idx in job_used:
                new_inv[idx]["qty"] = int(new_inv[idx].get("qty", 1)) - 1
            inv_save([r for r in new_inv if int(r.get("qty", 1)) > 0] + job_left)
            st.session_state.job = []; st.session_state.calc = False
            st.session_state.inv_msg = (f"Job finished. Removed {len(job_used)} used stock piece(s) "
                                        f"and saved {len(job_left)} leftover(s) to the inventory.")
            st.rerun()

def inventory_page():
    import streamlit as st
    st.header("Inventory & ideas")
    st.caption("Add the sheets and offcuts you own, tick the ones you want to use, "
               "and get product ideas. No job needed.")
    ver = st.session_state.setdefault("inv_ver", 0)

    with st.expander("1. Add stock", expanded=not inv_load()):
        c = st.columns(5)
        mat = c[0].selectbox("Material", [B18, B6])
        kind = c[1].selectbox("Type", KINDS)
        L = c[2].number_input("Length (mm)", 50, 6000, 2440)
        Wd = c[3].number_input("Width (mm)", 50, 3000, 1220)
        q = c[4].number_input("Quantity", 1, 500, 1)
        label = st.text_input("Label (optional)", placeholder="e.g. Supplier A, shelf 2")
        if st.button("Add to inventory", type="primary"):
            inv_add([dict(label=label, material=mat, kind=kind, length=max(L, Wd),
                          width=min(L, Wd), qty=q)])
            st.session_state.inv_ver += 1
            st.rerun()

    inv = inv_load()
    if not inv:
        st.info("Your inventory is empty. Add a sheet size above to get started.")
        return

    st.subheader("2. Your inventory")
    sel_all = st.checkbox("Select everything for ideas", False)
    df = pd.DataFrame(inv, columns=["label", "material", "kind", "length", "width", "qty"])
    df.insert(0, "Use", sel_all)
    cc = st.column_config
    edited = st.data_editor(
        df, key=f"inv_{ver}_{sel_all}", num_rows="dynamic", hide_index=True,
        column_config={"Use": cc.CheckboxColumn("Use for ideas"),
                       "label": cc.TextColumn("Label"),
                       "material": cc.SelectboxColumn("Material", options=[B18, B6], required=True),
                       "kind": cc.SelectboxColumn("Type", options=KINDS, required=True),
                       "length": cc.NumberColumn("Length (mm)", min_value=50, step=1),
                       "width": cc.NumberColumn("Width (mm)", min_value=50, step=1),
                       "qty": cc.NumberColumn("Qty", min_value=1, step=1)})
    cur = inv_clean(edited)
    m1, m2, m3 = st.columns(3)
    m1.metric("Stock lines", len(cur))
    m2.metric("Pieces in stock", sum(r["qty"] for r in cur))
    m3.metric("Total area", f"{sum(r['length'] * r['width'] * r['qty'] for r in cur) / 1e6:.1f} m2")
    if st.button("Save changes to inventory"):
        inv_save(cur)
        st.session_state.inv_ver += 1
        st.rerun()
    st.caption("Edit cells directly. Select a row and press Delete to remove it. "
               "Click 'Save changes' to keep edits.")

    st.subheader("3. Ideas from the stock you ticked")
    c1, c2 = st.columns(2)
    kerf = c1.number_input("Blade thickness (mm)", 0, 10, 3, key="inv_kerf")
    rotate = c2.checkbox("Allow rotating pieces (off for wood grain)", True, key="inv_rot")
    chosen = inv_clean(edited[edited["Use"] == True])  # noqa: E712
    if not chosen:
        st.info("Tick 'Use for ideas' on one or more rows to see what you can make.")
        return
    for m in dict.fromkeys(r["material"] for r in chosen):
        rects = [(0, 0, r["length"], r["width"]) for r in chosen if r["material"] == m
                 for _ in range(min(r["qty"], 50))]
        st.markdown(f"**{m}** - {len(rects)} piece(s) selected")
        show_ideas(m, rects, kerf, rotate, cap=24)

def main():
    import streamlit as st
    st.set_page_config(page_title="Waste Reducer", layout="wide")
    st.title("Smart Raw Material Waste Reducer")
    with st.sidebar:
        mode = st.radio("Mode", ["Cutting planner", "Inventory & ideas"])
        st.divider()
    if mode == "Inventory & ideas":
        inventory_page()
    else:
        planner_page()

if __name__ == "__main__":
    main()