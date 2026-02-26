"""
Standalone script: generate a fully-routed KiCad PCB with 361 SK6812 LEDs +
361 decoupling capacitors in a 19x19 serpentine layout.

Additions vs. v1 (placement-only):
  - Full netlist (GND, VDD, DIN_IN, DATA_1…DATA_361)
  - Collision-safe data-chain routing (3-case L/R/wrap routing)
  - GND vias connecting F.Cu GND pads to B.Cu GND zone
  - Full-board VDD zone (F.Cu) + GND zone (B.Cu)
  - Connectors J1 (input) and J2 (output)
  - Zone fill before save

Requires KiCad to be installed (uses KiCad's bundled pcbnew Python module).

Usage (macOS):
    KICAD_PY="/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9"
    cd electronics/kicad_files/19x19
    $KICAD_PY scripts/generate_19x19.py

Output: electronics/kicad_files/19x19/saiboard_19x19.kicad_pcb
"""

import sys
import os
import platform

# ---------------------------------------------------------------------------
# Step 1: Find and load pcbnew (KiCad's Python module)
# ---------------------------------------------------------------------------

def find_pcbnew():
    """Add KiCad's Python site-packages to sys.path and return pcbnew module."""

    try:
        import pcbnew
        return pcbnew
    except ImportError:
        pass

    system = platform.system()
    candidate_paths = []

    if system == "Darwin":  # macOS
        base = "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework"
        for pyver in ["3.11", "3.10", "3.9", "3.12"]:
            candidate_paths.append(
                f"{base}/Versions/{pyver}/lib/python{pyver}/site-packages"
            )
        candidate_paths.append(
            "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework"
            "/Versions/Current/lib/python3.9/site-packages"
        )

    elif system == "Linux":
        for pyver in ["3", "3.11", "3.10", "3.9"]:
            candidate_paths += [
                f"/usr/lib/python{pyver}/dist-packages",
                f"/usr/lib/python{pyver}/site-packages",
                f"/usr/local/lib/python{pyver}/dist-packages",
            ]
        candidate_paths.append(
            os.path.expanduser("~/.local/share/flatpak/exports/lib/python3/site-packages")
        )

    elif system == "Windows":
        for ver in ["9.0", "8.0", "7.0"]:
            root = f"C:\\Program Files\\KiCad\\{ver}"
            candidate_paths += [
                f"{root}\\lib\\python3\\site-packages",
                f"{root}\\bin",
            ]

    for path in candidate_paths:
        if os.path.isdir(path):
            sys.path.insert(0, path)
            try:
                import pcbnew
                print(f"[ok] pcbnew loaded from: {path}")
                return pcbnew
            except ImportError:
                sys.path.pop(0)

    print("ERROR: Could not find pcbnew.")
    print("  Make sure KiCad is installed, then set PYTHONPATH manually.")
    sys.exit(1)


pcbnew = find_pcbnew()
print(f"[ok] KiCad build: {pcbnew.GetBuildVersion()}")

# ---------------------------------------------------------------------------
# Step 2: Find KiCad footprint library directory
# ---------------------------------------------------------------------------

def find_fp_library_root():
    """Return the root directory that contains LED_SMD.pretty, etc."""

    system = platform.system()
    candidates = []

    if system == "Darwin":
        candidates = [
            "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints",
        ]
    elif system == "Linux":
        candidates = [
            "/usr/share/kicad/footprints",
            "/usr/local/share/kicad/footprints",
        ]
    elif system == "Windows":
        for ver in ["9.0", "8.0", "7.0"]:
            candidates.append(f"C:\\Program Files\\KiCad\\{ver}\\share\\kicad\\footprints")

    for path in candidates:
        if os.path.isdir(os.path.join(path, "LED_SMD.pretty")):
            print(f"[ok] footprint library root: {path}")
            return path

    print("ERROR: KiCad footprint library not found.")
    print("  Set FP_ROOT environment variable to the folder containing LED_SMD.pretty")
    sys.exit(1)


FP_ROOT = os.environ.get("FP_ROOT") or find_fp_library_root()

LED_LIB = os.path.join(FP_ROOT, "LED_SMD.pretty")
CAP_LIB = os.path.join(FP_ROOT, "Capacitor_SMD.pretty")
CON_LIB = os.path.join(FP_ROOT, "Connector_PinHeader_2.54mm.pretty")

LED_FP = "LED_SK6812_PLCC4_5.0x5.0mm_P3.2mm"
CAP_FP = "C_1206_3216Metric"
CON_FP = "PinHeader_1x03_P2.54mm_Vertical"

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------

START_X   = 30.0   # mm – X of D1 (top-left LED)
START_Y   = 30.0   # mm – Y of D1
SPACING_X = 22.0   # mm – horizontal spacing
SPACING_Y = 23.7   # mm – vertical spacing
ROWS      = 19
COLS      = 19
CAP_DX    = 4.0    # mm – capacitor offset right of its LED
CAP_DY    = 0.0    # mm – capacitor vertical offset

BOARD_W = START_X + (COLS - 1) * SPACING_X + START_X   # 426 mm
BOARD_H = START_Y + (ROWS - 1) * SPACING_Y + START_Y   # 486.6 mm

OUTPUT_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "saiboard_19x19.kicad_pcb")

# ---------------------------------------------------------------------------
# Helper: compute LED / cap X,Y (mm) from 1-based serial number n
# ---------------------------------------------------------------------------

def led_position_mm(n):
    """Return (x_mm, y_mm) of the n-th LED (1-based, serpentine order)."""
    row = (n - 1) // COLS
    col_in_row = (n - 1) % COLS
    actual_col = col_in_row if row % 2 == 0 else (COLS - 1 - col_in_row)
    return START_X + actual_col * SPACING_X, START_Y + row * SPACING_Y


def cap_position_mm(n):
    lx, ly = led_position_mm(n)
    return lx + CAP_DX, ly


def pad_xy_mm(pad_obj):
    """Return (x_mm, y_mm) of a pad's absolute board position."""
    pos = pad_obj.GetPosition()
    return pcbnew.ToMM(pos.x), pcbnew.ToMM(pos.y)

# ---------------------------------------------------------------------------
# Step 3: Load template footprints from library
# ---------------------------------------------------------------------------

print(f"Loading LED footprint  : {LED_FP}")
led_template = pcbnew.FootprintLoad(LED_LIB, LED_FP)
if not led_template:
    print(f"ERROR: Could not load {LED_FP} from {LED_LIB}")
    sys.exit(1)

print(f"Loading cap footprint  : {CAP_FP}")
cap_template = pcbnew.FootprintLoad(CAP_LIB, CAP_FP)
if not cap_template:
    print(f"ERROR: Could not load {CAP_FP} from {CAP_LIB}")
    sys.exit(1)

print(f"Loading connector footprint: {CON_FP}")
con_template = pcbnew.FootprintLoad(CON_LIB, CON_FP)
if not con_template:
    print(f"WARNING: Could not load {CON_FP} from {CON_LIB} — connectors will be skipped")

# ---------------------------------------------------------------------------
# Step 4: Create board
# ---------------------------------------------------------------------------

board = pcbnew.BOARD()

margin = pcbnew.FromMM(0.05)
for (x1, y1), (x2, y2) in [
    ((0, 0),             (BOARD_W, 0)),
    ((BOARD_W, 0),       (BOARD_W, BOARD_H)),
    ((BOARD_W, BOARD_H), (0, BOARD_H)),
    ((0, BOARD_H),       (0, 0)),
]:
    seg = pcbnew.PCB_SHAPE(board)
    seg.SetShape(pcbnew.SHAPE_T_SEGMENT)
    seg.SetLayer(pcbnew.Edge_Cuts)
    seg.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
    seg.SetEnd(pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
    seg.SetWidth(margin)
    board.Add(seg)

# ---------------------------------------------------------------------------
# Step 5: Place 361 LEDs + 361 capacitors in serpentine order
# ---------------------------------------------------------------------------

n = 0
for row in range(ROWS):
    for col in range(COLS):
        actual_col = col if row % 2 == 0 else (COLS - 1 - col)
        n += 1

        x   = pcbnew.FromMM(START_X + actual_col * SPACING_X)
        y   = pcbnew.FromMM(START_Y + row * SPACING_Y)
        cdx = pcbnew.FromMM(CAP_DX)
        cdy = pcbnew.FromMM(CAP_DY)

        led = pcbnew.FOOTPRINT(led_template)
        led.SetReference(f"D{n}")
        led.SetPosition(pcbnew.VECTOR2I(x, y))
        led.Reference().SetVisible(False)
        led.Value().SetVisible(False)
        board.Add(led)

        cap = pcbnew.FOOTPRINT(cap_template)
        cap.SetReference(f"C{n}")
        cap.SetPosition(pcbnew.VECTOR2I(x + cdx, y + cdy))
        cap.Reference().SetVisible(False)
        cap.Value().SetVisible(False)
        board.Add(cap)

        if n % 50 == 0:
            print(f"  placed {n}/361 ...")

print(f"  placed all 361 LEDs and capacitors")

# ---------------------------------------------------------------------------
# Step 6b: Define nets  (no manual net codes — let KiCad assign them)
# ---------------------------------------------------------------------------

print("Creating nets ...")

def create_net(brd, name):
    net = pcbnew.NETINFO_ITEM(brd, name)
    brd.Add(net)
    return net

net_gnd    = create_net(board, "GND")
net_vdd    = create_net(board, "VDD")
net_din_in = create_net(board, "DIN_IN")

data_nets = [create_net(board, f"DATA_{i}") for i in range(1, 362)]
# data_nets[0] = DATA_1 … data_nets[360] = DATA_361

print(f"  {len(data_nets) + 3} nets created")

# ---------------------------------------------------------------------------
# Step 6c: Build pad lookup:  ref -> {pad_number_str -> pad_object}
# ---------------------------------------------------------------------------

pad_map = {}
for fp in board.GetFootprints():
    ref = fp.GetReference()
    pad_map[ref] = {}
    for pad in fp.Pads():
        pad_map[ref][str(pad.GetNumber())] = pad   # str() for KiCad 7/8 compat

# ---------------------------------------------------------------------------
# Step 6d: Assign nets to pads
# ---------------------------------------------------------------------------

print("Assigning nets to pads ...")
for n in range(1, 362):
    pads  = pad_map.get(f"D{n}", {})
    cpads = pad_map.get(f"C{n}", {})

    if "1" in pads:  pads["1"].SetNet(net_gnd)
    if "2" in pads:  pads["2"].SetNet(net_din_in if n == 1 else data_nets[n - 2])
    if "3" in pads:  pads["3"].SetNet(net_vdd)
    if "4" in pads:  pads["4"].SetNet(data_nets[n - 1])

    if "1" in cpads: cpads["1"].SetNet(net_vdd)
    if "2" in cpads: cpads["2"].SetNet(net_gnd)

print("  Nets assigned.")

# ---------------------------------------------------------------------------
# Step 6e: Route data chain — read real pad positions, handle 3 cases
#
# Three cases to avoid shorts:
#   A) Same row, L→R: route via channel ABOVE the row (y - 0.4*SPACING_Y)
#   B) Same row, R→L: route via channel BELOW the row (y + 0.4*SPACING_Y)
#   C) Row wrap (different rows): route via mid-gap between the two rows
# ---------------------------------------------------------------------------

DATA_WIDTH_MM = 0.25

def add_track(brd, x1, y1, x2, y2, net, width_mm, layer=pcbnew.F_Cu):
    if abs(x1 - x2) < 1e-6 and abs(y1 - y2) < 1e-6:
        return
    t = pcbnew.PCB_TRACK(brd)
    t.SetStart(pcbnew.VECTOR2I(pcbnew.FromMM(x1), pcbnew.FromMM(y1)))
    t.SetEnd(  pcbnew.VECTOR2I(pcbnew.FromMM(x2), pcbnew.FromMM(y2)))
    t.SetNet(net)
    t.SetWidth(pcbnew.FromMM(width_mm))
    t.SetLayer(layer)
    brd.Add(t)


def route_data(brd, dout_pad, din_pad, net, w, row_n, row_np1):
    """Route DOUT→DIN with collision-safe 3-segment dog-leg."""
    ox, oy = pad_xy_mm(dout_pad)
    ix, iy = pad_xy_mm(din_pad)

    if row_n == row_np1:
        # Same row — use horizontal channel safely above or below row centre
        row_centre_y = START_Y + row_n * SPACING_Y
        ltr = (row_n % 2 == 0)
        if ltr:
            mid_y = row_centre_y - SPACING_Y * 0.4   # above row (pads at ±1.6, safe ≥ 9mm away)
        else:
            mid_y = row_centre_y + SPACING_Y * 0.4   # below row
    else:
        # Row wrap — use mid-gap between the two rows
        y_row_n   = START_Y + row_n   * SPACING_Y
        y_row_np1 = START_Y + row_np1 * SPACING_Y
        mid_y = (y_row_n + y_row_np1) / 2.0

    add_track(brd, ox, oy, ox, mid_y, net, w)        # vertical from DOUT
    add_track(brd, ox, mid_y, ix, mid_y, net, w)      # horizontal in safe channel
    add_track(brd, ix, mid_y, ix, iy, net, w)         # vertical to DIN


print("Routing data chain ...")
skipped = 0
for n in range(1, 361):
    dout_pad = pad_map.get(f"D{n}",   {}).get("4")
    din_pad  = pad_map.get(f"D{n+1}", {}).get("2")
    if not dout_pad or not din_pad:
        print(f"  WARNING: pad missing for D{n}→D{n+1}, skipping")
        skipped += 1
        continue

    row_n   = (n - 1) // COLS
    row_np1 = n       // COLS

    route_data(board, dout_pad, din_pad, data_nets[n - 1],
               DATA_WIDTH_MM, row_n, row_np1)

    if n % 50 == 0:
        print(f"  routed {n}/360 ...")

print(f"  Data chain routing done. ({360 - skipped} connections)")

# ---------------------------------------------------------------------------
# Step 6e2: Add GND vias — one per LED Pad1 (GND) + one per Cap Pad2 (GND)
#           Connects F.Cu SMD GND pads to B.Cu GND zone
# ---------------------------------------------------------------------------

VIA_DRILL_MM = 0.4
VIA_SIZE_MM  = 0.8   # annular ring = (0.8-0.4)/2 = 0.2mm

print("Adding GND vias ...")
via_count = 0

def add_gnd_via(brd, x_mm, y_mm, gnd_net):
    via = pcbnew.PCB_VIA(brd)
    via.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm)))
    via.SetWidth(pcbnew.FromMM(VIA_SIZE_MM))
    via.SetDrill(pcbnew.FromMM(VIA_DRILL_MM))
    via.SetNet(gnd_net)
    via.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
    brd.Add(via)

for n in range(1, 362):
    p_led_gnd = pad_map.get(f"D{n}", {}).get("1")
    if p_led_gnd:
        px, py = pad_xy_mm(p_led_gnd)
        add_gnd_via(board, px + 1.0, py, net_gnd)
        via_count += 1

    p_cap_gnd = pad_map.get(f"C{n}", {}).get("2")
    if p_cap_gnd:
        px, py = pad_xy_mm(p_cap_gnd)
        add_gnd_via(board, px + 1.0, py, net_gnd)
        via_count += 1

print(f"  {via_count} GND vias added.")

# ---------------------------------------------------------------------------
# Step 6f: Add copper zones — VDD on F.Cu, GND on B.Cu
# ---------------------------------------------------------------------------

print("Adding power zones ...")

ZONE_CLS = pcbnew.ZONE if hasattr(pcbnew, "ZONE") else pcbnew.ZONE_CONTAINER

def add_full_board_zone(brd, layer, net, w, h):
    zone = ZONE_CLS(brd)
    zone.SetLayer(layer)
    zone.SetNet(net)
    zone.SetIsRuleArea(False)
    zone.SetLocalClearance(pcbnew.FromMM(0.2))
    zone.SetMinThickness(pcbnew.FromMM(0.2))
    outline = zone.Outline()
    outline.NewOutline()
    for px, py in [(0, 0), (w, 0), (w, h), (0, h)]:
        outline.Append(pcbnew.FromMM(px), pcbnew.FromMM(py))
    brd.Add(zone)
    return zone

zone_vdd = add_full_board_zone(board, pcbnew.F_Cu, net_vdd, BOARD_W, BOARD_H)
zone_gnd = add_full_board_zone(board, pcbnew.B_Cu, net_gnd, BOARD_W, BOARD_H)
print("  VDD zone (F.Cu) and GND zone (B.Cu) added.")

# ---------------------------------------------------------------------------
# Step 6g: Place connectors J1 (input) and J2 (output)
# ---------------------------------------------------------------------------

if con_template is not None:
    print("Placing connectors J1 and J2 ...")

    def place_connector(brd, ref, x_mm, y_mm, rotation_deg,
                        p1_net, p2_net, p3_net):
        fp = pcbnew.FOOTPRINT(con_template)
        fp.SetReference(ref)
        fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x_mm), pcbnew.FromMM(y_mm)))
        fp.SetOrientationDegrees(rotation_deg)
        fp.Reference().SetVisible(True)
        brd.Add(fp)
        for pad in fp.Pads():
            pnum = str(pad.GetNumber())
            if pnum == "1":   pad.SetNet(p1_net)
            elif pnum == "2": pad.SetNet(p2_net)
            elif pnum == "3": pad.SetNet(p3_net)
        return fp

    j1_x = START_X - 15.0
    j1_y = START_Y
    place_connector(board, "J1", j1_x, j1_y, 0,
                    net_din_in, net_gnd, net_vdd)

    d361_x, d361_y = led_position_mm(361)
    j2_x = d361_x + 15.0
    j2_y = d361_y
    place_connector(board, "J2", j2_x, j2_y, 0,
                    data_nets[360], net_gnd, net_vdd)

    print(f"  J1 placed at ({j1_x:.1f}, {j1_y:.1f}) mm")
    print(f"  J2 placed at ({j2_x:.1f}, {j2_y:.1f}) mm")
else:
    print("WARNING: Connectors skipped (footprint not found).")

# ---------------------------------------------------------------------------
# Step 6h: Fill zones and save
# ---------------------------------------------------------------------------

board.Save(OUTPUT_FILE)

# NOTE: ZONE_FILLER causes a hard segfault in KiCad 9 headless Python on macOS.
# Zones are fully defined (net + outline) and will be filled when you open the PCB
# in KiCad and press 'B' (Edit → Fill All Zones). Do this BEFORE exporting Gerbers.
print("  Zones defined (unfilled). Open PCB in KiCad and press 'B' to fill before Gerber export.")

# Patch paper size to A0 — pcbnew Python bindings don't expose PAGE_INFO
with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace('(paper "A4")', '(paper "A0")', 1)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print()
print(f"Done! {ROWS*COLS} LEDs (D1–D{ROWS*COLS}) and capacitors (C1–C{ROWS*COLS}) placed.")
print(f"Board size : {BOARD_W:.1f} x {BOARD_H:.1f} mm")
print(f"Output     : {OUTPUT_FILE}")
print()
print("Spot-check positions:")
print(f"  D1   → ({START_X:.1f}, {START_Y:.1f}) mm  (top-left)")
print(f"  D19  → ({START_X + 18 * SPACING_X:.1f}, {START_Y:.1f}) mm  (top-right)")
print(f"  D20  → ({START_X + 18 * SPACING_X:.1f}, {START_Y + SPACING_Y:.1f}) mm  (row 1 right)")
print(f"  D38  → ({START_X:.1f}, {START_Y + SPACING_Y:.1f}) mm  (row 1 left)")
print(f"  D361 → ({START_X + 18 * SPACING_X:.1f}, {START_Y + 18 * SPACING_Y:.1f}) mm  (bottom-right)")
