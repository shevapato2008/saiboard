"""
KiCad Python script: auto-place 361 SK6812 LEDs + 361 decoupling capacitors
in a 19x19 serpentine layout for the Saiboard Go board PCB.

Usage:
  1. In KiCad, manually place two template footprints:
       D1  - LED_SMD:LED_SK6812_PLCC4_5.0x5.0mm_P3.2mm
       C1  - Capacitor_SMD:C_0402_1005Metric
     (position doesn't matter; the script will move them)

  2. Open Tools → Scripting Console, paste this file's contents, and run.

Layout (serpentine):
  Row 0 (even) → D1   D2   D3  ... D19
  Row 1 (odd)  ← D38  D37  ... ... D20
  Row 2 (even) → D39  D40  ... ... D57
  ...
  Row 18 (even)→ D343 ... ... ... D361
"""

import pcbnew

# ---------------------------------------------------------------------------
# Parameters (edit as needed)
# ---------------------------------------------------------------------------
START_X = 30.0   # mm – X position of D1 (top-left LED)
START_Y = 30.0   # mm – Y position of D1 (top-left LED)
SPACING = 22.5   # mm – Go board standard intersection spacing
ROWS    = 19
COLS    = 19
CAP_DX  = 4.0    # mm – capacitor X offset relative to its LED
CAP_DY  = 0.0    # mm – capacitor Y offset relative to its LED
# ---------------------------------------------------------------------------

board = pcbnew.GetBoard()


def find_fp(ref):
    """Return the footprint with the given reference, or None."""
    for fp in board.GetFootprints():
        if fp.GetReference() == ref:
            return fp
    return None


d1 = find_fp("D1")
c1 = find_fp("C1")

if not d1 or not c1:
    missing = []
    if not d1:
        missing.append("D1")
    if not c1:
        missing.append("C1")
    print(f"ERROR: Template footprint(s) not found: {', '.join(missing)}")
    print("Please place D1 (SK6812) and C1 (0402 cap) on the board first.")
else:
    n = 0
    for row in range(ROWS):
        for col in range(COLS):
            # Serpentine: reverse column order on odd rows
            actual_col = col if row % 2 == 0 else (COLS - 1 - col)
            n += 1

            x   = pcbnew.FromMM(START_X + actual_col * SPACING)
            y   = pcbnew.FromMM(START_Y + row * SPACING)
            cdx = pcbnew.FromMM(CAP_DX)
            cdy = pcbnew.FromMM(CAP_DY)

            if n == 1:
                # Move templates to their correct position
                d1.SetPosition(pcbnew.VECTOR2I(x, y))
                c1.SetPosition(pcbnew.VECTOR2I(x + cdx, y + cdy))
            else:
                # Duplicate templates and assign new references
                led = d1.Duplicate()
                led.SetReference(f"D{n}")
                led.SetPosition(pcbnew.VECTOR2I(x, y))
                board.Add(led)

                cap = c1.Duplicate()
                cap.SetReference(f"C{n}")
                cap.SetPosition(pcbnew.VECTOR2I(x + cdx, y + cdy))
                board.Add(cap)

    pcbnew.Refresh()
    board.Save(board.GetFileName())
    print(f"Done! Placed {n} LEDs (D1–D{n}) and {n} capacitors (C1–C{n}).")
    print()
    print("Verify:")
    print(f"  D1  → ({START_X:.1f}, {START_Y:.1f}) mm  (top-left)")
    print(f"  D19 → ({START_X + 18 * SPACING:.1f}, {START_Y:.1f}) mm  (top-right)")
    print(f"  D20 → ({START_X + 18 * SPACING:.1f}, {START_Y + SPACING:.1f}) mm  (row 1 right)")
    print(f"  D38 → ({START_X:.1f}, {START_Y + SPACING:.1f}) mm  (row 1 left)")
