"""
Standalone script: generate a KiCad PCB with 361 SK6812 LEDs + 361 decoupling
capacitors in a 19x19 serpentine layout.

Requires KiCad to be installed (uses KiCad's bundled pcbnew Python module).

Usage:
    # macOS (most common)
    python3 generate_19x19.py

    # Linux
    python3 generate_19x19.py

    # Windows (PowerShell)
    & "C:\\Program Files\\KiCad\\7.0\\bin\\python.exe" generate_19x19.py

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

    # If already importable (e.g. running inside KiCad or pcbnew in PATH), use it
    try:
        import pcbnew
        return pcbnew
    except ImportError:
        pass

    system = platform.system()

    candidate_paths = []

    if system == "Darwin":  # macOS
        # KiCad 8 / 9
        base = "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework"
        for pyver in ["3.11", "3.10", "3.9", "3.12"]:
            candidate_paths.append(
                f"{base}/Versions/{pyver}/lib/python{pyver}/site-packages"
            )
        # KiCad 7 uses a different layout
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
        # Flatpak KiCad
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
    print("  Make sure KiCad is installed, then set PYTHONPATH manually:")
    print("  macOS:  export PYTHONPATH=/Applications/KiCad/KiCad.app/Contents/Frameworks/")
    print("          Python.framework/Versions/Current/lib/python3.x/site-packages")
    sys.exit(1)


pcbnew = find_pcbnew()

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
LED_FP  = "LED_SK6812_PLCC4_5.0x5.0mm_P3.2mm"
CAP_FP  = "C_1206_3216Metric"

# ---------------------------------------------------------------------------
# Parameters (edit as needed)
# ---------------------------------------------------------------------------

START_X    = 30.0   # mm – X of D1 (top-left LED)
START_Y    = 30.0   # mm – Y of D1
SPACING_X  = 22.0   # mm – horizontal spacing (matches 8x8/11x3/3x8/8x3 sub-boards)
SPACING_Y  = 23.7   # mm – vertical spacing   (matches 8x8/11x3/3x8/8x3 sub-boards)
ROWS       = 19
COLS       = 19
CAP_DX     = 4.0    # mm – capacitor offset right of its LED
CAP_DY     = 0.0    # mm – capacitor offset below its LED

BOARD_W    = START_X + (COLS - 1) * SPACING_X + START_X   # 426 mm
BOARD_H    = START_Y + (ROWS - 1) * SPACING_Y + START_Y   # 486.6 mm

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)  # electronics/kicad_files/19x19/
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "saiboard_19x19.kicad_pcb")

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

# ---------------------------------------------------------------------------
# Step 4: Create board
# ---------------------------------------------------------------------------

board = pcbnew.BOARD()

# Board outline on Edge_Cuts layer (4 line segments — more reliable than SHAPE_T_RECT)
margin = pcbnew.FromMM(0.05)
for (x1, y1), (x2, y2) in [
    ((0, 0),        (BOARD_W, 0)),       # top
    ((BOARD_W, 0),  (BOARD_W, BOARD_H)), # right
    ((BOARD_W, BOARD_H), (0, BOARD_H)),  # bottom
    ((0, BOARD_H),  (0, 0)),             # left
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

        # LED
        led = pcbnew.FOOTPRINT(led_template)   # deep copy
        led.SetReference(f"D{n}")
        led.SetPosition(pcbnew.VECTOR2I(x, y))
        led.Reference().SetVisible(False)
        led.Value().SetVisible(False)
        board.Add(led)

        # Capacitor
        cap = pcbnew.FOOTPRINT(cap_template)   # deep copy
        cap.SetReference(f"C{n}")
        cap.SetPosition(pcbnew.VECTOR2I(x + cdx, y + cdy))
        cap.Reference().SetVisible(False)
        cap.Value().SetVisible(False)
        board.Add(cap)

        if n % 50 == 0:
            print(f"  placed {n}/361 ...")

# ---------------------------------------------------------------------------
# Step 6: Save
# ---------------------------------------------------------------------------

board.Save(OUTPUT_FILE)

# Patch paper size to A0 (1189x841mm) — large enough to display the 465x465mm board
# pcbnew Python bindings don't expose PAGE_INFO, so we edit the file directly
with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace('(paper "A4")', '(paper "A0")', 1)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(content)

print()
print(f"Done! {n} LEDs (D1–D{n}) and {n} capacitors (C1–C{n}) placed.")
print(f"Board size : {BOARD_W:.1f} x {BOARD_H:.1f} mm")
print(f"Output     : {OUTPUT_FILE}")
print()
print("Spot-check positions:")
print(f"  D1   → ({START_X:.1f}, {START_Y:.1f}) mm  (top-left)")
print(f"  D19  → ({START_X + 18 * SPACING_X:.1f}, {START_Y:.1f}) mm  (top-right)")
print(f"  D20  → ({START_X + 18 * SPACING_X:.1f}, {START_Y + SPACING_Y:.1f}) mm  (row 1 right)")
print(f"  D38  → ({START_X:.1f}, {START_Y + SPACING_Y:.1f}) mm  (row 1 left)")
print(f"  D361 → ({START_X + 18 * SPACING_X:.1f}, {START_Y + 18 * SPACING_Y:.1f}) mm  (bottom-right)")
