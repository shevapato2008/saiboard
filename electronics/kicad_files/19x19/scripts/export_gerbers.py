"""
Export JLCPCB-ready Gerber + Excellon drill files from saiboard_19x19.kicad_pcb.

Usage (macOS):
    KICAD_PY="/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/3.9/bin/python3.9"
    cd electronics/kicad_files/19x19
    $KICAD_PY scripts/export_gerbers.py

Output: electronics/kicad_files/19x19/production/
"""

import sys
import os
import platform

# ---------------------------------------------------------------------------
# Locate pcbnew
# ---------------------------------------------------------------------------

def find_pcbnew():
    try:
        import pcbnew
        return pcbnew
    except ImportError:
        pass

    system = platform.system()
    paths = []

    if system == "Darwin":
        base = "/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework"
        for v in ["3.11", "3.10", "3.9", "3.12"]:
            paths.append(f"{base}/Versions/{v}/lib/python{v}/site-packages")

    elif system == "Linux":
        for v in ["3.11", "3.10", "3.9", "3"]:
            paths += [
                f"/usr/lib/python{v}/dist-packages",
                f"/usr/lib/python{v}/site-packages",
            ]

    elif system == "Windows":
        for ver in ["9.0", "8.0", "7.0"]:
            paths.append(f"C:\\Program Files\\KiCad\\{ver}\\lib\\python3\\site-packages")

    for p in paths:
        if os.path.isdir(p):
            sys.path.insert(0, p)
            try:
                import pcbnew
                print(f"[ok] pcbnew loaded from: {p}")
                return pcbnew
            except ImportError:
                sys.path.pop(0)

    print("ERROR: pcbnew not found. Install KiCad.")
    sys.exit(1)


pcbnew = find_pcbnew()
print(f"[ok] KiCad build: {pcbnew.GetBuildVersion()}")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PCB_DIR    = os.path.dirname(SCRIPT_DIR)          # …/19x19/
PCB_FILE   = os.path.join(PCB_DIR, "saiboard_19x19.kicad_pcb")
OUTPUT_DIR = os.path.join(PCB_DIR, "production")

if not os.path.isfile(PCB_FILE):
    print(f"ERROR: PCB file not found: {PCB_FILE}")
    print("  Run generate_19x19.py first.")
    sys.exit(1)

os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Loading PCB : {PCB_FILE}")
board = pcbnew.LoadBoard(PCB_FILE)

# ---------------------------------------------------------------------------
# Gerber plot
# ---------------------------------------------------------------------------

plot_ctrl = pcbnew.PLOT_CONTROLLER(board)
plot_opts = plot_ctrl.GetPlotOptions()

plot_opts.SetOutputDirectory(OUTPUT_DIR)
plot_opts.SetPlotFrameRef(False)
# SetExcludeEdgeLayer removed in KiCad 9 — Edge.Cuts exported as its own layer
plot_opts.SetUseGerberX2format(False)          # classic X1 — JLCPCB compatible
plot_opts.SetIncludeGerberNetlistInfo(False)
plot_opts.SetUseAuxOrigin(False)
plot_opts.SetGerberPrecision(5)                # 5-decimal coordinate precision
plot_opts.SetSubtractMaskFromSilk(True)

LAYERS = [
    (pcbnew.F_Cu,     "F_Cu"),
    (pcbnew.B_Cu,     "B_Cu"),
    (pcbnew.F_Mask,   "F_Mask"),
    (pcbnew.B_Mask,   "B_Mask"),
    (pcbnew.F_SilkS,  "F_SilkS"),
    (pcbnew.B_SilkS,  "B_SilkS"),
    (pcbnew.Edge_Cuts, "Edge_Cuts"),
]

print(f"Exporting Gerbers to: {OUTPUT_DIR}")
for layer_id, layer_name in LAYERS:
    plot_ctrl.SetLayer(layer_id)
    plot_ctrl.OpenPlotfile(layer_name, pcbnew.PLOT_FORMAT_GERBER, layer_name)
    plot_ctrl.PlotLayer()
    print(f"  [{layer_name}] written")

plot_ctrl.ClosePlot()

# ---------------------------------------------------------------------------
# Excellon drill file
# ---------------------------------------------------------------------------

drill_writer = pcbnew.EXCELLON_WRITER(board)
drill_writer.SetOptions(
    False,                         # mirror Y
    True,                          # minimal header
    pcbnew.VECTOR2I(0, 0),         # origin
    True                           # merge PTH + NPTH
)
drill_writer.SetFormat(True, pcbnew.EXCELLON_WRITER.DECIMAL_FORMAT, 3, 3)
drill_writer.CreateDrillandMapFilesSet(OUTPUT_DIR, True, False)
print("  [Drill] .drl written")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------

files = sorted(os.listdir(OUTPUT_DIR))
print(f"\nProduction files ({len(files)} total):")
for fname in files:
    fpath = os.path.join(OUTPUT_DIR, fname)
    size  = os.path.getsize(fpath)
    print(f"  {fname:<40}  {size:>10,} bytes")

print()
print("Done. ZIP the production/ folder and upload to JLCPCB.")
print(f"  cd {OUTPUT_DIR} && zip ../saiboard_19x19_gerbers.zip *.gbr *.drl")
