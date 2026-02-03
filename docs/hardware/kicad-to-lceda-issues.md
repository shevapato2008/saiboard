# KiCad 转嘉立创 EDA 问题记录

本文档记录了 8×8 子板 PCB 从 KiCad 导入嘉立创 EDA（LCEDA Pro）过程中遇到的问题，以及嘉立创工厂审核反馈的错误分析。

## 背景

8×8 子板原始设计在 KiCad 中完成（`electronics/kicad_files/8x8/`）。为提交嘉立创 SMT 生产，使用 KiCad 嘉立创 Fabrication Toolkit 插件将项目转换格式后导入嘉立创 EDA，在嘉立创 EDA 中修改原理图和 PCB 并通过 DRC 后，导出 Gerber 提交生产。

## 工厂反馈

嘉立创审核反馈：**"PCB 资料可能有误，线路层是连到一起的。"**

即：铜层上存在大面积短路，不同网络的走线被铜皮连接在了一起。

## 根因分析

### 1. 铺铜网络分配错误（核心问题）

在嘉立创 EDA 的 PCB 中，顶层和底层的铺铜填充（Copper Pour）被分配到了 **`POWER_PWR_FLAG`** 网络，而非正确的 `GND`。

`POWER_PWR_FLAG` 是 KiCad 中的虚拟 ERC 辅助网络，由 `PWR_FLAG` 符号产生，**仅用于消除电气规则检查（ERC）警告**，不是一个真正的电气网络。KiCad → 嘉立创 EDA 转换过程中，这个虚拟网络被当作了真实网络处理。

**验证数据：**

| 项目 | 数值 |
| :--- | :--- |
| 顶层 Gerber (GTL) 铺铜多边形行数 | ~17,778 行（覆盖整板） |
| 底层 Gerber (GBL) 铺铜多边形行数 | ~9,117 行（覆盖整板） |
| LCEDA 备份中 `POWER_PWR_FLAG` 引用次数 | 1,759 |
| LCEDA 备份中 `GND` 引用次数 | 136 |
| LCEDA 备份中 `P`（VDD）引用次数 | 71 |
| KiCad 原始 PCB 中铺铜区域（Zone）数量 | **0**（无铺铜） |

### 2. 网络映射大面积错乱

`POWER_PWR_FLAG` 在 LCEDA 备份中有 1,759 次引用，远超 `GND` 的 136 次。这表明大量元件引脚在转换过程中被错误地分配到了 `POWER_PWR_FLAG` 网络。

由于铺铜网络也是 `POWER_PWR_FLAG`，铺铜通过热焊盘将这些引脚全部连接在一起，导致本应独立的信号线（如不同 Hall 传感器输出、LED DIN/DOUT 链路）被铺铜短接。

### 3. 原始 KiCad 设计无铺铜

原始 KiCad PCB 文件 (`8x8.kicad_pcb`) 中没有定义任何 Zone（铺铜区域），也不存在 `POWER_PWR_FLAG` 网络。正确的网络定义为：

- `net 1 "P"` — 电源（VDD）
- `net 10 "GND"` — 地

铺铜区域是在导入嘉立创 EDA 后新增的，但网络被错误地设置为 `POWER_PWR_FLAG`。

## 影响

整板顶层和底层被一个错误网络的铺铜覆盖，所有接入 `POWER_PWR_FLAG` 网络的焊盘通过铺铜短接，导致 PCB 无法正常工作。

## 修复方案

### 方案 A：在嘉立创 EDA 中修复

1. 打开 PCB 编辑器
2. 选中顶层和底层的铺铜区域，将网络从 `POWER_PWR_FLAG` 改为 `GND`
3. **逐一核对所有元件引脚的网络分配**，将错误分配到 `POWER_PWR_FLAG` 的引脚修正回正确网络（`GND`、`P` 等）
4. 重新铺铜
5. 重新运行 DRC，确认无错
6. 重新导出 Gerber

### 方案 B：回到 KiCad 直接导出（推荐）

原始 KiCad 设计本身没有铺铜，无需添加。直接从 KiCad 导出即可：

1. 在 KiCad 原理图中**删除 11 个悬空的 PWR_FLAG 符号**（位于原理图左上角区域，未连接任何导线）
2. 运行 ERC 确认无新增错误
3. 直接从 KiCad 使用嘉立创 Fabrication Toolkit 导出 Gerber、BOM、坐标文件
4. **不再经过嘉立创 EDA 二次编辑**，避免转换引入的网络映射问题

> 注：铺铜（GND Copper Pour）可以改善接地质量和 EMI 性能，但原始设计未使用，属于可选改进。如需添加，在 KiCad PCB 中操作（Add Filled Zone → 选 GND 网络），不要在嘉立创 EDA 中添加。

## 经验教训

1. **KiCad → 嘉立创 EDA 转换不可靠**：`PWR_FLAG` 等 KiCad 特有的 ERC 辅助符号会被嘉立创 EDA 误解为真实网络，导致网络映射错乱。
2. **铺铜网络必须手动确认**：添加铺铜后务必检查网络分配是否正确，不能仅依赖 DRC（DRC 可能不会检测铺铜网络分配语义错误）。
3. **减少工具链切换**：尽量在同一 EDA 工具中完成设计全流程，避免跨工具转换引入隐蔽错误。如必须转换，需逐网络核对映射结果。
4. **对比 Gerber 和原始设计**：提交生产前，在 Gerber 查看器中确认铜层没有异常大面积铜皮。

## 相关文件

| 文件 | 说明 |
| :--- | :--- |
| `electronics/kicad_files/8x8/` | KiCad 原始设计文件 |
| `~/Downloads/Gerber_8x8_2026-01-31/` | 提交给嘉立创的 Gerber 文件（有问题） |
| `~/Downloads/BOM_智能棋盘8x8_2026-01-31.xlsx` | BOM 文件 |
| `~/Downloads/PickAndPlace_智能棋盘8x8_2026_01_31.xlsx` | 坐标文件 |
| `~/Documents/LCEDA-Pro/projects/led-hall-8x8_*` | 嘉立创 EDA 项目文件及备份 |
