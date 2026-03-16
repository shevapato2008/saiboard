#!/usr/bin/env python3
"""Verify the diagonal LED strip mapping for the 19x19 Saiboard.

The LED strip follows anti-diagonals (d = row - col + 18), starting at [0,18] (d=0),
zigzagging across the board toward [18,0] (d=36). Each turn between diagonals wastes
2 LEDs (physically present but not on any intersection).

Usage:
    python verify_led_mapping.py                # print full 19x19 grid + validation
    python verify_led_mapping.py 0 18           # single lookup: row=0 col=18
    python verify_led_mapping.py --diagonals    # print all 37 diagonals with details
"""

import sys


def diagonal_size(d):
    """Number of active LEDs on diagonal d (0..36)."""
    if d <= 18:
        return d + 1
    else:
        return 37 - d


def diagonal_start(d):
    """Starting LED index for diagonal d."""
    if d <= 18:
        return 3 * d + d * (d - 1) // 2
    else:
        return 438 - (39 - d) * (40 - d) // 2


def row_col_to_led(row, col):
    """Map board position (row, col) to LED strip index."""
    d = row - col + 18

    if d <= 18:
        if d % 2 == 0:
            pos = row
        else:
            pos = d - row
    else:
        if d % 2 == 0:
            pos = row - (d - 18)
        else:
            pos = 18 - row

    return diagonal_start(d) + pos


def print_grid():
    """Print the full 19x19 mapping grid."""
    print("LED index grid (row 0 = top, col 0 = left):\n")
    print("     ", end="")
    for c in range(19):
        print(f"{c:>4}", end="")
    print()
    print("     ", end="")
    print("----" * 19)
    for r in range(19):
        print(f"{r:>3} |", end="")
        for c in range(19):
            print(f"{row_col_to_led(r, c):>4}", end="")
        print()


def print_diagonals():
    """Print all 37 diagonals with LED indices, waste LEDs, and coordinates."""
    cumulative = 0
    print(f"{'d':>3}  {'size':>4}  {'start':>5}  {'end':>5}  {'waste':>5}  direction  cells")
    print("-" * 80)
    for d in range(37):
        size = diagonal_size(d)
        start = diagonal_start(d)
        end = start + size - 1
        waste_start = end + 1 if d < 36 else None
        direction = "↘ (even)" if d % 2 == 0 else "↗ (odd) "

        # Build cell list
        cells = []
        if d <= 18:
            rows = range(0, d + 1) if d % 2 == 0 else range(d, -1, -1)
        else:
            rows = range(d - 18, 19) if d % 2 == 0 else range(18, d - 19, -1)
        for r in rows:
            c = r - d + 18
            cells.append(f"[{r},{c}]")

        waste_str = f"{end+1}-{end+2}" if d < 36 else "none"
        print(f"{d:>3}  {size:>4}  {start:>5}  {end:>5}  {waste_str:>5}  {direction}  {', '.join(cells)}")
        cumulative = end + 1 + (2 if d < 36 else 0)

    print(f"\nTotal LEDs on strip: 361 active + 72 waste = 433")


def validate():
    """Validate all 361 positions map to unique indices in [0, 432]."""
    seen = set()
    errors = []
    for r in range(19):
        for c in range(19):
            led = row_col_to_led(r, c)
            if led < 0 or led > 432:
                errors.append(f"[{r},{c}] -> {led} OUT OF RANGE")
            if led in seen:
                errors.append(f"[{r},{c}] -> {led} DUPLICATE")
            seen.add(led)

    # Check known positions from the plan
    checks = [
        (0, 18, 0),
        (1, 18, 3), (0, 17, 4),
        (0, 16, 7), (1, 17, 8), (2, 18, 9),
        (3, 18, 12), (0, 15, 15),
    ]
    for r, c, expected in checks:
        actual = row_col_to_led(r, c)
        if actual != expected:
            errors.append(f"[{r},{c}] expected {expected}, got {actual}")

    if errors:
        print("VALIDATION FAILED:")
        for e in errors:
            print(f"  {e}")
        return False
    else:
        print(f"VALIDATION PASSED: 361 unique LED indices in [0, 432]")
        # Show waste LED indices
        all_leds = {row_col_to_led(r, c) for r in range(19) for c in range(19)}
        waste = sorted(set(range(433)) - all_leds)
        print(f"  Waste LED indices ({len(waste)}): {waste}")
        return True


def main():
    if len(sys.argv) == 3 and sys.argv[1] != "--diagonals":
        row, col = int(sys.argv[1]), int(sys.argv[2])
        print(f"[{row},{col}] -> LED {row_col_to_led(row, col)}")
    elif len(sys.argv) == 2 and sys.argv[1] == "--diagonals":
        print_diagonals()
    else:
        print_grid()
        print()
        validate()


if __name__ == "__main__":
    main()
