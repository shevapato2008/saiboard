# LED 对角线走线映射 / Diagonal LED Strip Mapping

## 概述 / Overview

LED 灯带沿 **反对角线** (anti-diagonal) 布线，从右上角 `[0,18]` 开始，锯齿形走向左下角 `[18,0]`。每条对角线之间的转弯浪费 2 颗 LED（物理存在但不对应棋盘交叉点）。

The LED strip follows anti-diagonals starting from top-right `[0,18]`, zigzagging diagonally across the board toward `[18,0]`. Each turn between diagonals wastes 2 LEDs (physically present on the strip but not aligned with any board intersection).

## 灯带参数 / Strip Parameters

| 参数                       | 旧值   | 新值          |
| -------------------------- | ------ | ------------- |
| `strip.length`           | 361    | **433** |
| 有效 LED / Active LEDs     | 361    | 361           |
| 废弃 LED / Waste LEDs      | 0      | 72 (36×2)    |
| LED 索引范围 / Index range | 0–360 | 0–432        |

## 映射算法 / Mapping Algorithm

### 对角线定义 / Diagonal Definition

共 37 条反对角线 (d = 0..36)，由 `d = row - col + 18` 定义。

- d=0 仅含 `[0,18]`（1 颗 LED）
- d=18 为主对角线，含 19 颗 LED（`[0,0]` 到 `[18,18]`）
- d=36 仅含 `[18,0]`（1 颗 LED）

### 对角线大小 / Diagonal Size

```
d ≤ 18:  size(d) = d + 1
d > 18:  size(d) = 37 - d
```

### 锯齿方向 / Zigzag Direction

- **偶数 d (0,2,4,...)**：↘ 方向（row 递增）
- **奇数 d (1,3,5,...)**：↗ 方向（row 递减）

### 起始 LED 索引 / Starting LED Index

```
d ≤ 18:  start(d) = 3d + d(d-1)/2
d > 18:  start(d) = 438 - (39-d)(40-d)/2
```

### 对角线内位置 / Position Within Diagonal

```
d ≤ 18, 偶数:  pos = row
d ≤ 18, 奇数:  pos = d - row
d > 18, 偶数:  pos = row - (d - 18)
d > 18, 奇数:  pos = 18 - row
```

**LED 索引 = start(d) + pos**

### C 实现 / C Implementation

```c
int _row_col_to_nr(int row, int col)
{
    int d = row - col + 18;
    int start, pos;

    if (d <= 18)
    {
        start = 3 * d + d * (d - 1) / 2;
        pos = (d % 2 == 0) ? row : (d - row);
    }
    else
    {
        start = 438 - (39 - d) * (40 - d) / 2;
        pos = (d % 2 == 0) ? (row - (d - 18)) : (18 - row);
    }

    return start + pos;
}
```

## 关键位置参考 / Key Position Reference

| 棋盘位置    | LED 索引 | 对角线 | 说明             |
| ----------- | -------- | ------ | ---------------- |
| `[0,18]`  | 0        | d=0    | 右上角，灯带起点 |
| `[1,18]`  | 3        | d=1    |                  |
| `[0,17]`  | 4        | d=1    |                  |
| `[0,16]`  | 7        | d=2    |                  |
| `[1,17]`  | 8        | d=2    |                  |
| `[2,18]`  | 9        | d=2    |                  |
| `[3,18]`  | 12       | d=3    |                  |
| `[0,15]`  | 15       | d=3    |                  |
| `[0,0]`   | 207      | d=18   | 左上角           |
| `[9,9]`   | 216      | d=18   | 天元（棋盘中心） |
| `[18,18]` | 225      | d=18   | 右下角           |
| `[18,0]`  | 432      | d=36   | 左下角，灯带终点 |

## 37 条对角线完整枚举 / Full Diagonal Enumeration

```
  d  size  start   end  waste   方向      首尾坐标
  0     1      0     0    1-2   ↘ even    [0,18]
  1     2      3     4    5-6   ↗ odd     [1,18] → [0,17]
  2     3      7     9  10-11   ↘ even    [0,16] → [2,18]
  3     4     12    15  16-17   ↗ odd     [3,18] → [0,15]
  4     5     18    22  23-24   ↘ even    [0,14] → [4,18]
  5     6     25    30  31-32   ↗ odd     [5,18] → [0,13]
  6     7     33    39  40-41   ↘ even    [0,12] → [6,18]
  7     8     42    49  50-51   ↗ odd     [7,18] → [0,11]
  8     9     52    60  61-62   ↘ even    [0,10] → [8,18]
  9    10     63    72  73-74   ↗ odd     [9,18] → [0,9]
 10    11     75    85  86-87   ↘ even    [0,8]  → [10,18]
 11    12     88    99 100-101  ↗ odd     [11,18]→ [0,7]
 12    13    102   114 115-116  ↘ even    [0,6]  → [12,18]
 13    14    117   130 131-132  ↗ odd     [13,18]→ [0,5]
 14    15    133   147 148-149  ↘ even    [0,4]  → [14,18]
 15    16    150   165 166-167  ↗ odd     [15,18]→ [0,3]
 16    17    168   184 185-186  ↘ even    [0,2]  → [16,18]
 17    18    187   204 205-206  ↗ odd     [17,18]→ [0,1]
 18    19    207   225 226-227  ↘ even    [0,0]  → [18,18]
 19    18    228   245 246-247  ↗ odd     [18,17]→ [1,0]
 20    17    248   264 265-266  ↘ even    [2,0]  → [18,16]
 21    16    267   282 283-284  ↗ odd     [18,15]→ [3,0]
 22    15    285   299 300-301  ↘ even    [4,0]  → [18,14]
 23    14    302   315 316-317  ↗ odd     [18,13]→ [5,0]
 24    13    318   330 331-332  ↘ even    [6,0]  → [18,12]
 25    12    333   344 345-346  ↗ odd     [18,11]→ [7,0]
 26    11    347   357 358-359  ↘ even    [8,0]  → [18,10]
 27    10    360   369 370-371  ↗ odd     [18,9] → [9,0]
 28     9    372   380 381-382  ↘ even    [10,0] → [18,8]
 29     8    383   390 391-392  ↗ odd     [18,7] → [11,0]
 30     7    393   399 400-401  ↘ even    [12,0] → [18,6]
 31     6    402   407 408-409  ↗ odd     [18,5] → [13,0]
 32     5    410   414 415-416  ↘ even    [14,0] → [18,4]
 33     4    417   420 421-422  ↗ odd     [18,3] → [15,0]
 34     3    423   425 426-427  ↘ even    [16,0] → [18,2]
 35     2    428   429 430-431  ↗ odd     [18,1] → [17,0]
 36     1    432   432   none   ↘ even    [18,0]
```

## 文件说明 / File Reference

| 文件                      | 说明                     |
| ------------------------- | ------------------------ |
| `main/main.c`           | 原始固件（三段竖直走线） |
| `main/main-new.c`       | 新固件（对角线走线）     |
| `verify_led_mapping.py` | Python 验证脚本          |

### 验证脚本用法 / Verification Script Usage

#### led mapping

```bash
# 打印 19×19 完整映射表 + 验证
python3 led_mapping.py

# 查询单个位置
python3 led_mapping.py 0 18    # → LED 0
python3 led_mapping.py 9 9     # → LED 216

# 打印所有对角线详情
python3 led_mapping.py --diagonals
```

#### led reverse mapping

```bash
python3 led_reverse_mapping.py 0      # → LED 0 → [018]                                                                                                           
python3 led_reverse_mapping.py 5      # → LED 5 → waste                                                                                                            
python3 led_reverse_mapping.py --all  # 打印完整 0..432 
```

## nc 测试命令 / Test Commands

JSON 命令格式不变：`[row, col, r, g, b, w]`

```bash
# 右上角 [0,18] 红色
echo '{"name":"led","leds":[[0,18,255,0,0,0]]}' | nc 192.168.4.1 3333

# 天元 [9,9] 白色
echo '{"name":"led","leds":[[9,9,0,0,0,255]]}' | nc 192.168.4.1 3333

# 左下角 [18,0] 蓝色
echo '{"name":"led","leds":[[18,0,0,0,255,0]]}' | nc 192.168.4.1 3333

# 四角同时点亮
echo '{"name":"led","leds":[[0,0,255,0,0,0],[0,18,0,255,0,0],[18,0,0,0,255,0],[18,18,0,0,0,255]]}' | nc 192.168.4.1 3333
```

## 影响范围 / Impact

仅固件 `_row_col_to_nr()` 函数和 `strip.length` 需要修改。后端 (`board.py`, `play.py`) 发送的是 `[row, col]` 坐标，映射由 ESP32 处理，无需改动。
