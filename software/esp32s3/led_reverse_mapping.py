#!/usr/bin/env python3
"""Reverse LED strip mapping: given LED index, return board coordinate.

Usage:
    python reverse_led_mapping.py 0        # → [0,18]
    python reverse_led_mapping.py 4        # → [0,17]
    python reverse_led_mapping.py 5        # → waste LED
    python reverse_led_mapping.py --all    # print full strip 0..432
"""

import sys


def diagonal_size(d):
    return d + 1 if d <= 18 else 37 - d


def diagonal_start(d):
    if d <= 18:
        return 3 * d + d * (d - 1) // 2
    else:
        return 438 - (39 - d) * (40 - d) // 2


def row_col_to_led(row, col):
    d = row - col + 18
    if d <= 18:
        start = 3 * d + d * (d - 1) // 2
        pos = row if d % 2 == 0 else d - row
    else:
        start = 438 - (39 - d) * (40 - d) // 2
        pos = row - (d - 18) if d % 2 == 0 else 18 - row
    return start + pos


def build_reverse_map():
    """Build dict: LED index -> (row, col) or None for waste LEDs."""
    reverse = {}
    for r in range(19):
        for c in range(19):
            led = row_col_to_led(r, c)
            reverse[led] = (r, c)
    return reverse


def led_to_row_col(led_index, reverse_map):
    """Return (row, col) tuple or None if waste LED."""
    return reverse_map.get(led_index)


def print_all(reverse_map):
    """Print the full strip from LED 0 to 432."""
    print(f"{'LED':>5}  {'坐标':>8}  {'类型'}")
    print("-" * 30)
    for i in range(433):
        coord = reverse_map.get(i)
        if coord:
            r, c = coord
            print(f"{i:>5}  [{r:>2},{c:>2}]  active")
        else:
            print(f"{i:>5}  {'---':>8}  waste")


def main():
    reverse_map = build_reverse_map()

    if len(sys.argv) == 2 and sys.argv[1] == "--all":
        print_all(reverse_map)
    elif len(sys.argv) == 2:
        led_index = int(sys.argv[1])
        if led_index < 0 or led_index > 432:
            print(f"LED {led_index} out of range [0, 432]")
            sys.exit(1)
        coord = reverse_map.get(led_index)
        if coord:
            r, c = coord
            print(f"LED {led_index} → [{r},{c}]")
        else:
            print(f"LED {led_index} → waste (无棋盘坐标)")
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
