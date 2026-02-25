"""
Generate saiboard_19x19.kicad_sch – a 19×19 SK6812 LED serpentine schematic.

Layout
------
- Even rows (0,2,4,…): mirror y, LEDs left→right (D1..D19, D39..D57, …)
- Odd  rows (1,3,5,…): mirror x, LEDs right→left (D38..D20, D76..D58, …)
- Each LED has a 100 nF decoupling capacitor placed below it.
- Global labels "P" and "GND" form the power nets.
- Data chain: explicit wire segments DOUT→DIN within rows and vertical
  wires between rows.

Output: electronics/kicad_files/19x19/saiboard_19x19.kicad_sch
"""

import uuid
import os

# ---------------------------------------------------------------------------
# Parameters
# ---------------------------------------------------------------------------
ROWS               = 19
COLS               = 19
SCH_LED_SPACING_X  = 28.0      # mm – horizontal spacing between LED centres
SCH_ROW_SPACING    = 50.0      # mm – vertical spacing between row centres
CAP_OFFSET_Y       = 15.0      # mm – cap centre below LED centre
START_X            = 50.0      # mm – X of D1 centre
START_Y            = 50.0      # mm – Y of D1 centre

PAPER_W = 700.0
PAPER_H = 1060.0

OUTPUT_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "saiboard_19x19.kicad_sch")

PIN_OFFSET     = 7.62   # mm – LED pin distance from centre
CAP_PIN_OFFSET = 3.81   # mm – Device:C pin distance from centre

# ---------------------------------------------------------------------------
# UUID helpers
# ---------------------------------------------------------------------------
def uid():
    return str(uuid.uuid4())

SCH_UUID = uid()

# ---------------------------------------------------------------------------
# Accumulate output lines
# ---------------------------------------------------------------------------
lines = []

def w(s=""):
    lines.append(s)

# ---------------------------------------------------------------------------
# Helper: global_label
# ---------------------------------------------------------------------------
def global_label(name, x, y, angle=180, justify="right"):
    w(f'  (global_label "{name}" (shape input) (at {x:.4f} {y:.4f} {angle}) (fields_autoplaced)')
    w(f'    (effects (font (size 1.27 1.27)) (justify {justify}))')
    w(f'    (uuid {uid()})')
    w(f'    (property "Intersheet References" "${{INTERSHEET_REFS}}" (id 0) (at {x:.4f} {y:.4f} 0)')
    w(f'      (effects (font (size 1.27 1.27)) hide)')
    w(f'    )')
    w(f'  )')
    w()

# ---------------------------------------------------------------------------
# Helper: wire segment
# ---------------------------------------------------------------------------
def wire(x1, y1, x2, y2):
    if abs(x1 - x2) < 0.001 and abs(y1 - y2) < 0.001:
        return   # skip zero-length wires
    w(f'  (wire (pts (xy {x1:.4f} {y1:.4f}) (xy {x2:.4f} {y2:.4f}))')
    w(f'    (stroke (width 0) (type default) (color 0 0 0 0))')
    w(f'    (uuid {uid()})')
    w(f'  )')
    w()

# ---------------------------------------------------------------------------
# symbol_instances list  (filled during emission)
# ---------------------------------------------------------------------------
sym_instances = []   # list of (sym_uuid, reference, value, footprint)

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
w(f'(kicad_sch (version 20211123) (generator eeschema)')
w()
w(f'  (uuid {SCH_UUID})')
w()
w(f'  (paper "User" {PAPER_W:.3f} {PAPER_H:.3f})')
w()

# ---------------------------------------------------------------------------
# lib_symbols  – Device:C, LED:SK6812, Connector_Generic:Conn_01x03
# ---------------------------------------------------------------------------
w('  (lib_symbols')

# ── Connector_Generic:Conn_01x03 ──────────────────────────────────────────
w('    (symbol "Connector_Generic:Conn_01x03" (pin_names (offset 1.016) hide) (in_bom yes) (on_board yes)')
w('      (property "Reference" "J" (id 0) (at 0 5.08 0)')
w('        (effects (font (size 1.27 1.27)))')
w('      )')
w('      (property "Value" "Conn_01x03" (id 1) (at 0 -5.08 0)')
w('        (effects (font (size 1.27 1.27)))')
w('      )')
w('      (property "Footprint" "" (id 2) (at 0 0 0)')
w('        (effects (font (size 1.27 1.27)) hide)')
w('      )')
w('      (property "Datasheet" "~" (id 3) (at 0 0 0)')
w('        (effects (font (size 1.27 1.27)) hide)')
w('      )')
w('      (property "ki_keywords" "connector" (id 4) (at 0 0 0)')
w('        (effects (font (size 1.27 1.27)) hide)')
w('      )')
w('      (property "ki_description" "Generic connector, single row, 01x03" (id 5) (at 0 0 0)')
w('        (effects (font (size 1.27 1.27)) hide)')
w('      )')
w('      (property "ki_fp_filters" "Connector*:*_1x??_*" (id 6) (at 0 0 0)')
w('        (effects (font (size 1.27 1.27)) hide)')
w('      )')
w('      (symbol "Conn_01x03_1_1"')
w('        (rectangle (start -1.27 -2.413) (end 0 -2.667)')
w('          (stroke (width 0.1524) (type default) (color 0 0 0 0))')
w('          (fill (type none))')
w('        )')
w('        (rectangle (start -1.27 0.127) (end 0 -0.127)')
w('          (stroke (width 0.1524) (type default) (color 0 0 0 0))')
w('          (fill (type none))')
w('        )')
w('        (rectangle (start -1.27 2.667) (end 0 2.413)')
w('          (stroke (width 0.1524) (type default) (color 0 0 0 0))')
w('          (fill (type none))')
w('        )')
w('        (rectangle (start -1.27 3.81) (end 1.27 -3.81)')
w('          (stroke (width 0.254) (type default) (color 0 0 0 0))')
w('          (fill (type background))')
w('        )')
w('        (pin passive line (at -5.08 2.54 0) (length 3.81)')
w('          (name "Pin_1" (effects (font (size 1.27 1.27))))')
w('          (number "1" (effects (font (size 1.27 1.27))))')
w('        )')
w('        (pin passive line (at -5.08 0 0) (length 3.81)')
w('          (name "Pin_2" (effects (font (size 1.27 1.27))))')
w('          (number "2" (effects (font (size 1.27 1.27))))')
w('        )')
w('        (pin passive line (at -5.08 -2.54 0) (length 3.81)')
w('          (name "Pin_3" (effects (font (size 1.27 1.27))))')
w('          (number "3" (effects (font (size 1.27 1.27))))')
w('        )')
w('      )')
w('    )')

# ── Device:C ──────────────────────────────────────────────────────────────
w('    (symbol "Device:C" (pin_numbers hide) (pin_names (offset 0.254)) (in_bom yes) (on_board yes)')
w('      (property "Reference" "C" (id 0) (at 0.635 2.54 0)')
w('        (effects (font (size 1.27 1.27)) (justify left))')
w('      )')
w('      (property "Value" "C" (id 1) (at 0.635 -2.54 0)')
w('        (effects (font (size 1.27 1.27)) (justify left))')
w('      )')
w('      (property "Footprint" "" (id 2) (at 0.9652 -3.81 0)')
w('        (effects (font (size 1.27 1.27)) hide)')
w('      )')
w('      (property "Datasheet" "~" (id 3) (at 0 0 0)')
w('        (effects (font (size 1.27 1.27)) hide)')
w('      )')
w('      (property "ki_keywords" "cap capacitor" (id 4) (at 0 0 0)')
w('        (effects (font (size 1.27 1.27)) hide)')
w('      )')
w('      (property "ki_description" "Unpolarized capacitor" (id 5) (at 0 0 0)')
w('        (effects (font (size 1.27 1.27)) hide)')
w('      )')
w('      (property "ki_fp_filters" "C_*" (id 6) (at 0 0 0)')
w('        (effects (font (size 1.27 1.27)) hide)')
w('      )')
w('      (symbol "C_0_1"')
w('        (polyline')
w('          (pts (xy -2.032 -0.762) (xy 2.032 -0.762))')
w('          (stroke (width 0.508) (type default) (color 0 0 0 0))')
w('          (fill (type none))')
w('        )')
w('        (polyline')
w('          (pts (xy -2.032 0.762) (xy 2.032 0.762))')
w('          (stroke (width 0.508) (type default) (color 0 0 0 0))')
w('          (fill (type none))')
w('        )')
w('      )')
w('      (symbol "C_1_1"')
w('        (pin passive line (at 0 3.81 270) (length 2.794)')
w('          (name "~" (effects (font (size 1.27 1.27))))')
w('          (number "1" (effects (font (size 1.27 1.27))))')
w('        )')
w('        (pin passive line (at 0 -3.81 90) (length 2.794)')
w('          (name "~" (effects (font (size 1.27 1.27))))')
w('          (number "2" (effects (font (size 1.27 1.27))))')
w('        )')
w('      )')
w('    )')

# ── LED:SK6812 ────────────────────────────────────────────────────────────
w('    (symbol "LED:SK6812" (pin_names (offset 0.254)) (in_bom yes) (on_board yes)')
w('      (property "Reference" "D" (id 0) (at 5.08 5.715 0)')
w('        (effects (font (size 1.27 1.27)) (justify right bottom))')
w('      )')
w('      (property "Value" "SK6812" (id 1) (at 1.27 -5.715 0)')
w('        (effects (font (size 1.27 1.27)) (justify left top))')
w('      )')
w('      (property "Footprint" "LED_SMD:LED_SK6812_PLCC4_5.0x5.0mm_P3.2mm" (id 2) (at 1.27 -7.62 0)')
w('        (effects (font (size 1.27 1.27)) (justify left top) hide)')
w('      )')
w('      (property "Datasheet" "https://cdn-shop.adafruit.com/product-files/1138/SK6812+LED+datasheet+.pdf" (id 3) (at 2.54 -9.525 0)')
w('        (effects (font (size 1.27 1.27)) (justify left top) hide)')
w('      )')
w('      (property "ki_keywords" "RGB LED NeoPixel addressable" (id 4) (at 0 0 0)')
w('        (effects (font (size 1.27 1.27)) hide)')
w('      )')
w('      (property "ki_description" "RGB LED with integrated controller" (id 5) (at 0 0 0)')
w('        (effects (font (size 1.27 1.27)) hide)')
w('      )')
w('      (property "ki_fp_filters" "LED*SK6812*PLCC*5.0x5.0mm*P3.2mm*" (id 6) (at 0 0 0)')
w('        (effects (font (size 1.27 1.27)) hide)')
w('      )')
w('      (symbol "SK6812_0_0"')
w('        (text "RGB" (at 2.286 -4.191 0)')
w('          (effects (font (size 0.762 0.762)))')
w('        )')
w('      )')
w('      (symbol "SK6812_0_1"')
w('        (polyline')
w('          (pts (xy 1.27 -3.556) (xy 1.778 -3.556))')
w('          (stroke (width 0) (type default) (color 0 0 0 0))')
w('          (fill (type none))')
w('        )')
w('        (polyline')
w('          (pts (xy 1.27 -2.54) (xy 1.778 -2.54))')
w('          (stroke (width 0) (type default) (color 0 0 0 0))')
w('          (fill (type none))')
w('        )')
w('        (polyline')
w('          (pts (xy 4.699 -3.556) (xy 2.667 -3.556))')
w('          (stroke (width 0) (type default) (color 0 0 0 0))')
w('          (fill (type none))')
w('        )')
w('        (polyline')
w('          (pts (xy 2.286 -2.54) (xy 1.27 -3.556) (xy 1.27 -3.048))')
w('          (stroke (width 0) (type default) (color 0 0 0 0))')
w('          (fill (type none))')
w('        )')
w('        (polyline')
w('          (pts (xy 2.286 -1.524) (xy 1.27 -2.54) (xy 1.27 -2.032))')
w('          (stroke (width 0) (type default) (color 0 0 0 0))')
w('          (fill (type none))')
w('        )')
w('        (polyline')
w('          (pts (xy 3.683 -1.016) (xy 3.683 -3.556) (xy 3.683 -4.064))')
w('          (stroke (width 0) (type default) (color 0 0 0 0))')
w('          (fill (type none))')
w('        )')
w('        (polyline')
w('          (pts (xy 4.699 -1.524) (xy 2.667 -1.524) (xy 3.683 -3.556) (xy 4.699 -1.524))')
w('          (stroke (width 0) (type default) (color 0 0 0 0))')
w('          (fill (type none))')
w('        )')
w('        (rectangle (start 5.08 5.08) (end -5.08 -5.08)')
w('          (stroke (width 0.254) (type default) (color 0 0 0 0))')
w('          (fill (type background))')
w('        )')
w('      )')
w('      (symbol "SK6812_1_1"')
w('        (pin power_in line (at 0 -7.62 90) (length 2.54)')
w('          (name "VSS" (effects (font (size 1.27 1.27))))')
w('          (number "1" (effects (font (size 1.27 1.27))))')
w('        )')
w('        (pin input line (at -7.62 0 0) (length 2.54)')
w('          (name "DIN" (effects (font (size 1.27 1.27))))')
w('          (number "2" (effects (font (size 1.27 1.27))))')
w('        )')
w('        (pin power_in line (at 0 7.62 270) (length 2.54)')
w('          (name "VDD" (effects (font (size 1.27 1.27))))')
w('          (number "3" (effects (font (size 1.27 1.27))))')
w('        )')
w('        (pin output line (at 7.62 0 180) (length 2.54)')
w('          (name "DOUT" (effects (font (size 1.27 1.27))))')
w('          (number "4" (effects (font (size 1.27 1.27))))')
w('        )')
w('      )')
w('    )')

w('  )')   # end lib_symbols
w()

# ---------------------------------------------------------------------------
# Compute LED placement (serpentine order matching PCB script)
# ---------------------------------------------------------------------------
# led_info[i] = (schematic_x, schematic_y, led_number, row_index)
led_info = []
for row in range(ROWS):
    for col in range(COLS):
        actual_col = col if row % 2 == 0 else (COLS - 1 - col)
        led_num = row * COLS + col + 1
        x = START_X + actual_col * SCH_LED_SPACING_X
        y = START_Y + row * SCH_ROW_SPACING
        led_info.append((x, y, led_num, row))

# ---------------------------------------------------------------------------
# Emit LED symbols + capacitors + power global labels
# ---------------------------------------------------------------------------
print("Emitting LED and capacitor symbols …")

for idx, (lx, ly, led_num, row) in enumerate(led_info):
    mirror = "y" if row % 2 == 0 else "x"

    led_uuid = uid()
    cap_uuid = uid()

    # -- LED pin UUIDs
    p1 = uid(); p2 = uid(); p3 = uid(); p4 = uid()

    # -- LED symbol instance
    w(f'  (symbol (lib_id "LED:SK6812") (at {lx:.4f} {ly:.4f} 0) (mirror {mirror}) (unit 1)')
    w(f'    (in_bom yes) (on_board yes)')
    w(f'    (uuid {led_uuid})')
    ref_y_off = -8.0
    w(f'    (property "Reference" "D{led_num}" (id 0) (at {lx:.4f} {ly + ref_y_off:.4f} 0)')
    w(f'      (effects (font (size 1.27 1.27)))')
    w(f'    )')
    w(f'    (property "Value" "SK6812" (id 1) (at {lx:.4f} {ly + 8.0:.4f} 0)')
    w(f'      (effects (font (size 1.27 1.27)) hide)')
    w(f'    )')
    w(f'    (property "Footprint" "LED_SMD:LED_SK6812_PLCC4_5.0x5.0mm_P3.2mm" (id 2) (at {lx:.4f} {ly:.4f} 0)')
    w(f'      (effects (font (size 1.27 1.27)) hide)')
    w(f'    )')
    w(f'    (property "Datasheet" "https://cdn-shop.adafruit.com/product-files/1138/SK6812+LED+datasheet+.pdf" (id 3) (at {lx:.4f} {ly:.4f} 0)')
    w(f'      (effects (font (size 1.27 1.27)) hide)')
    w(f'    )')
    w(f'    (pin "1" (uuid {p1}))')
    w(f'    (pin "2" (uuid {p2}))')
    w(f'    (pin "3" (uuid {p3}))')
    w(f'    (pin "4" (uuid {p4}))')
    w(f'  )')
    w()
    sym_instances.append((led_uuid, f'D{led_num}', 'SK6812',
                           'LED_SMD:LED_SK6812_PLCC4_5.0x5.0mm_P3.2mm'))

    # -- Capacitor (rotation 180°, placed CAP_OFFSET_Y below LED centre)
    cx, cy = lx, ly + CAP_OFFSET_Y
    cp1 = uid(); cp2 = uid()

    w(f'  (symbol (lib_id "Device:C") (at {cx:.4f} {cy:.4f} 180) (unit 1)')
    w(f'    (in_bom yes) (on_board yes) (fields_autoplaced)')
    w(f'    (uuid {cap_uuid})')
    w(f'    (property "Reference" "C{led_num}" (id 0) (at {cx + 3.5:.4f} {cy - 1.27:.4f} 0)')
    w(f'      (effects (font (size 1.27 1.27)) (justify left))')
    w(f'    )')
    w(f'    (property "Value" "C104" (id 1) (at {cx + 3.5:.4f} {cy + 1.27:.4f} 0)')
    w(f'      (effects (font (size 1.27 1.27)) (justify left))')
    w(f'    )')
    w(f'    (property "Footprint" "Capacitor_SMD:C_1206_3216Metric" (id 2) (at {cx:.4f} {cy:.4f} 0)')
    w(f'      (effects (font (size 1.27 1.27)) hide)')
    w(f'    )')
    w(f'    (property "Datasheet" "~" (id 3) (at {cx:.4f} {cy:.4f} 0)')
    w(f'      (effects (font (size 1.27 1.27)) hide)')
    w(f'    )')
    w(f'    (pin "1" (uuid {cp1}))')
    w(f'    (pin "2" (uuid {cp2}))')
    w(f'  )')
    w()
    sym_instances.append((cap_uuid, f'C{led_num}', 'C104',
                           'Capacitor_SMD:C_1206_3216Metric'))

    # ── Power labels ─────────────────────────────────────────────────────
    # LED pin positions after mirror transform:
    #   mirror y (even rows): VSS at Y-7.62 (above), VDD at Y+7.62 (below)
    #   mirror x (odd rows):  VSS at Y+7.62 (below), VDD at Y-7.62 (above)
    if row % 2 == 0:
        vss_y = ly - PIN_OFFSET   # above
        vdd_y = ly + PIN_OFFSET   # below
    else:
        vss_y = ly + PIN_OFFSET   # below
        vdd_y = ly - PIN_OFFSET   # above

    # "P" = power (+5V) at VDD pin, "GND" at VSS pin
    global_label("P",   lx, vdd_y, angle=180)
    global_label("GND", lx, vss_y, angle=180)

    # Cap rotation 180°: Pin1 is above cap (Y - 3.81), Pin2 is below (Y + 3.81)
    cap_top_y = cy - CAP_PIN_OFFSET    # pin1 after 180° → above cap
    cap_bot_y = cy + CAP_PIN_OFFSET    # pin2 after 180° → below cap
    global_label("P",   cx, cap_top_y, angle=180)
    global_label("GND", cx, cap_bot_y, angle=180)

    # Short wire connecting LED VDD to cap top pin (both in P net, but explicit wire)
    wire(lx, vdd_y, cx, cap_top_y)

    if (idx + 1) % 50 == 0:
        print(f"  {idx + 1}/361 …")

# ---------------------------------------------------------------------------
# Data chain wires (DOUT → DIN)
# ---------------------------------------------------------------------------
print("Emitting data chain wires …")

for idx in range(len(led_info)):
    lx, ly, led_num, row = led_info[idx]

    # DOUT offset for this row's mirror:
    #   mirror y (even): DIN at X-7.62, DOUT at X+7.62
    #   mirror x (odd):  DIN at X+7.62, DOUT at X-7.62
    if row % 2 == 0:
        dout_x = lx + PIN_OFFSET
    else:
        dout_x = lx - PIN_OFFSET
    dout_y = ly

    if idx >= len(led_info) - 1:
        continue   # last LED, no next

    nx, ny, _, nrow = led_info[idx + 1]

    if nrow == row:
        # Same row – horizontal wire DOUT → next DIN
        if nrow % 2 == 0:
            next_din_x = nx - PIN_OFFSET   # mirror y: DIN at left
        else:
            next_din_x = nx + PIN_OFFSET   # mirror x: DIN at right
        wire(dout_x, dout_y, next_din_x, ny)
    else:
        # Row transition – vertical wire at DOUT x position
        # The next row's first LED shares the same actual_col,
        # so its DIN x == dout_x (same pin-offset side)
        wire(dout_x, dout_y, dout_x, ny)

# ---------------------------------------------------------------------------
# Connectors J1 (input) and J2 (output)
# ---------------------------------------------------------------------------
# Conn_01x03 rotation 0° pin connection offsets (from symbol centre):
#   Pin 1 at (centre_x - 5.08,  centre_y + 2.54)
#   Pin 2 at (centre_x - 5.08,  centre_y + 0)
#   Pin 3 at (centre_x - 5.08,  centre_y - 2.54)

# J1 – placed to the left of D1
lx0, ly0, _, _ = led_info[0]
d1_din_x = lx0 - PIN_OFFSET   # D1 DIN (even row, mirror y)
d1_din_y = ly0

# J1 Pin1 must reach d1_din_x.  Place J1 so Pin1 is at (d1_din_x - 10, ly0)
# and add a horizontal wire to D1 DIN.
j1_pin1_x = d1_din_x - 10.0
j1_pin1_y = ly0
j1_x = j1_pin1_x + 5.08     # centre_x = pin1_x + 5.08  (since pin is at x-5.08)
j1_y = j1_pin1_y - 2.54     # centre_y = pin1_y - 2.54

j1_uuid = uid()
jp1 = uid(); jp2 = uid(); jp3 = uid()

w(f'  (symbol (lib_id "Connector_Generic:Conn_01x03") (at {j1_x:.4f} {j1_y:.4f} 0) (unit 1)')
w(f'    (in_bom yes) (on_board yes)')
w(f'    (uuid {j1_uuid})')
w(f'    (property "Reference" "J1" (id 0) (at {j1_x + 2:.4f} {j1_y - 5:.4f} 0)')
w(f'      (effects (font (size 1.27 1.27)))')
w(f'    )')
w(f'    (property "Value" "Conn_01x03" (id 1) (at {j1_x + 2:.4f} {j1_y + 5:.4f} 0)')
w(f'      (effects (font (size 1.27 1.27)) hide)')
w(f'    )')
w(f'    (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Horizontal_SMD" (id 2) (at {j1_x:.4f} {j1_y:.4f} 0)')
w(f'      (effects (font (size 1.27 1.27)) hide)')
w(f'    )')
w(f'    (property "Datasheet" "~" (id 3) (at {j1_x:.4f} {j1_y:.4f} 0)')
w(f'      (effects (font (size 1.27 1.27)) hide)')
w(f'    )')
w(f'    (pin "1" (uuid {jp1}))')
w(f'    (pin "2" (uuid {jp2}))')
w(f'    (pin "3" (uuid {jp3}))')
w(f'  )')
w()
sym_instances.append((j1_uuid, 'J1', 'Conn_01x03',
                       'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Horizontal_SMD'))

# Wire J1 Pin1 → D1 DIN
wire(j1_pin1_x, j1_pin1_y, d1_din_x, d1_din_y)
# J1 Pin2 (at j1_x-5.08, j1_y)   → P
# J1 Pin3 (at j1_x-5.08, j1_y-2.54) → GND
j1_p2_x = j1_x - 5.08
global_label("P",   j1_p2_x, j1_y,        angle=180)
global_label("GND", j1_p2_x, j1_y - 2.54, angle=180)

# J2 – placed to the right of D361 (last LED, even row 18, mirror y)
lx_last, ly_last, _, row_last = led_info[-1]
d361_dout_x = lx_last + PIN_OFFSET   # even row, DOUT at right
d361_dout_y = ly_last

# J2 rotation 0° placed so Pin1 is further right with a short wire gap
# Pin1 at (j2_x - 5.08, j2_y + 2.54)
j2_pin1_x = d361_dout_x + 10.0
j2_pin1_y = d361_dout_y
j2_x = j2_pin1_x + 5.08
j2_y = j2_pin1_y - 2.54

j2_uuid = uid()
jp1b = uid(); jp2b = uid(); jp3b = uid()

w(f'  (symbol (lib_id "Connector_Generic:Conn_01x03") (at {j2_x:.4f} {j2_y:.4f} 0) (unit 1)')
w(f'    (in_bom yes) (on_board yes)')
w(f'    (uuid {j2_uuid})')
w(f'    (property "Reference" "J2" (id 0) (at {j2_x + 2:.4f} {j2_y - 5:.4f} 0)')
w(f'      (effects (font (size 1.27 1.27)))')
w(f'    )')
w(f'    (property "Value" "Conn_01x03" (id 1) (at {j2_x + 2:.4f} {j2_y + 5:.4f} 0)')
w(f'      (effects (font (size 1.27 1.27)) hide)')
w(f'    )')
w(f'    (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Horizontal_SMD" (id 2) (at {j2_x:.4f} {j2_y:.4f} 0)')
w(f'      (effects (font (size 1.27 1.27)) hide)')
w(f'    )')
w(f'    (property "Datasheet" "~" (id 3) (at {j2_x:.4f} {j2_y:.4f} 0)')
w(f'      (effects (font (size 1.27 1.27)) hide)')
w(f'    )')
w(f'    (pin "1" (uuid {jp1b}))')
w(f'    (pin "2" (uuid {jp2b}))')
w(f'    (pin "3" (uuid {jp3b}))')
w(f'  )')
w()
sym_instances.append((j2_uuid, 'J2', 'Conn_01x03',
                       'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Horizontal_SMD'))

# Wire D361 DOUT → J2 Pin1
wire(d361_dout_x, d361_dout_y, j2_pin1_x, j2_pin1_y)
# J2 Pin2 (at j2_x-5.08, j2_y)   → P
# J2 Pin3 (at j2_x-5.08, j2_y-2.54) → GND
j2_p2_x = j2_x - 5.08
global_label("P",   j2_p2_x, j2_y,        angle=180)
global_label("GND", j2_p2_x, j2_y - 2.54, angle=180)

# ---------------------------------------------------------------------------
# symbol_instances section  (one path entry per component instance)
# ---------------------------------------------------------------------------
w('  (symbol_instances')
for sym_uuid, ref, val, fp in sym_instances:
    w(f'    (path "/{sym_uuid}"')
    w(f'      (reference "{ref}") (unit 1) (value "{val}") (footprint "{fp}")')
    w(f'    )')
w('  )')
w()
w(')')   # end kicad_sch

# ---------------------------------------------------------------------------
# Write output file
# ---------------------------------------------------------------------------
content = "\n".join(lines)
os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(content)

led_count = ROWS * COLS
print()
print(f"Done!")
print(f"  {led_count} LEDs   (D1–D{led_count})")
print(f"  {led_count} caps   (C1–C{led_count})")
print(f"  J1 (input), J2 (output)")
print(f"  Output: {OUTPUT_FILE}")
