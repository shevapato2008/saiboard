# Saiboard 硬件开发与生产指南

本指南旨在帮助开发者了解 Saiboard 项目中的工业生产模型，掌握相关软件工具的使用，并指导如何将设计转化为实物。

## 1. 硬件模型概览与背景知识

项目中的硬件设计分为三个核心部分：

### 1.1 棋盘结构 (Board Structure)
*   **模型位置**: `board/`
*   **文件格式**: `.f3d` (Fusion 360), `.dxf` (CAD 交换格式)
*   **背景知识**: 
    *   **木工与 CNC**: 棋盘框架由木材加工而成。`dxf` 文件用于激光切割或 CNC 铣削。
    *   **公差 (Tolerance)**: 硬件设计中必须考虑零件组装时的间隙，否则无法物理嵌入。
*   **软件**: **Autodesk Fusion 360**。
*   **作用**: 定义棋盘的物理外观、尺寸、传感器排布以及各部件的连接方式。

### 1.2 电子系统 (Electronics)
*   **模型位置**: `electronics/kicad_files/`, `electronics/3d_prints/`
*   **文件格式**: `.kicad_sch` / `.kicad_pcb` (KiCad), `.f3d`
*   **背景知识**:
    *   **PCB 设计**: 涉及电路原理图和印刷电路板布线。
    *   **霍尔传感器 (Hall Effect Sensor)**: 项目核心硬件，用于通过磁性检测棋子位置。
    *   **3D 打印遮罩**: 用于辅助固定传感器或遮挡光线。
*   **软件**: **KiCad**, **Fusion 360**。
*   **作用**: KiCad 负责电路逻辑和 PCB 生产；Fusion 360 负责设计 PCB 的支撑结构和外壳。

### 1.3 棋子与模具 (Stones & Molds)
*   **模型位置**: `stones/3d_prints/`
*   **文件格式**: `.f3d`
*   **背景知识**:
    *   **翻模灌浆**: 棋子是通过 3D 打印的模具翻模制作的，内埋磁铁。
*   **软件**: **Fusion 360**, **切片软件 (PrusaSlicer/Bambu Studio)**。
*   **作用**: 设计棋子的形态以及用于批量生产棋子的模具。

---

## 2. 核心软件工具链

| 软件 | 作用 | 备注 |
| :--- | :--- | :--- |
| **Autodesk Fusion 360** | **3D 建模 (CAD)**：查看、修改棋盘、支架、模具的所有 3D 模型。 | 工业标准，建议必装。 |
| **KiCad** | **电路设计 (EDA)**：打开 `.kicad_pcb` 文件，查看或修改电路板。 | 开源免费。 |
| **PrusaSlicer / Bambu Studio** | **3D 打印切片**：将 3D 模型转化为打印机识别的 `.gcode`。 | 准备打印实物的最后一步。 |
| **Inkscape / AutoCAD** | **矢量图处理**：查看或修改 `.dxf` 切割图。 | 处理 2D 零件（如棋盘面）。 |

---

## 3. 分步指导计划

### 第一步：查看模型 (2.1)

#### 详细文件清单 (Module File List)

以下是各模块的核心设计文件及其查看/编辑所需的软件：

**A. 棋盘结构 (Board Structure)**
主要涉及木工 CNC 加工和激光切割文件。

| 文件路径 | 文件名 | 说明 | 推荐软件 |
| :--- | :--- | :--- | :--- |
| `board/cnc_files/` | `Top.f3d` | 棋盘顶层面板的 3D 源文件，包含开孔和槽位设计。 | **Fusion 360** |
| | `top.dxf` | 用于激光切割或 CNC 的 2D 矢量图（顶层）。 | **AutoCAD** / **Inkscape** |
| | `grid.f3d` | 棋盘网格层的 3D 源文件（用于透光显示网格）。 | **Fusion 360** |
| | `grid.dxf` | 网格层的 2D 切割图。 | **AutoCAD** / **Inkscape** |
| | `bottom.f3d` | 棋盘底层背板的 3D 源文件。 | **Fusion 360** |
| | `bottom.dxf` | 底层背板的 2D 切割图。 | **AutoCAD** / **Inkscape** |
| | `side.f3d` / `side.dxf` | 棋盘侧边框的 3D 模型与 2D 切割图。 | **Fusion 360** / **AutoCAD** |
| `board/3d_prints/` | `pen_part1.f3d`, `pen_part2.f3d` | 辅助工具或装饰件的 3D 模型。 | **Fusion 360** |

**B. 电子系统 (Electronics)**
涉及 PCB 电路设计和电子元件的 3D 打印支架。

| 文件路径 | 文件名 | 说明 | 推荐软件 |
| :--- | :--- | :--- | :--- |
| `electronics/kicad_files/8x8/` | `8x8.kicad_pro` | 8x8 传感器阵列主板的项目文件。 | **KiCad** |
| | `8x8.kicad_pcb` | 8x8 主板的 PCB 布局文件。 | **KiCad** (PCB Editor) |
| | `8x8.kicad_sch` | 8x8 主板的电路原理图。 | **KiCad** (Schematic Editor) |
| `electronics/kicad_files/[11x3, 3x8, 8x3]/` | `*.kicad_pcb` | 边缘补丁板的 PCB 文件，用于拼接完整棋盘。 | **KiCad** |
| `electronics/3d_prints/` | `*_pcb_mask.f3d` | PCB 遮光罩与固定件的 3D 模型（如 `8x8_pcb_mask.f3d`）。 | **Fusion 360** |
| | `raspberry_pi_mount.f3d` | 树莓派固定支架的 3D 模型。 | **Fusion 360** |
| | `*.gcode` | 预先切片好的打印文件（针对特定打印机）。 | 直接导入 3D 打印机 (如 Prusa) |

**C. 棋子与模具 (Stones & Molds)**
涉及棋子翻模制作所需的 3D 打印模具。

| 文件路径 | 文件名 | 说明 | 推荐软件 |
| :--- | :--- | :--- | :--- |
| `stones/3d_prints/` | `go_stones_mold.f3d` | 棋子模具的 3D 源文件。 | **Fusion 360** |
| | `stone_holder.f3d` | 棋子收纳架或固定器的 3D 模型。 | **Fusion 360** |
| | `*.gcode` | 模具与收纳架的打印切片文件。 | 直接导入 3D 打印机 |

#### 操作演示
1.  **3D 模型**: 打开 Fusion 360，使用 `File -> Open` 打开 `board/cnc_files/top.f3d`。
    *   *操作技巧*: 按住鼠标中键平移，`Shift + 鼠标中键` 旋转，滚轮缩放。
2.  **电路板**: 打开 KiCad，进入 `PCB Editor` 载入 `electronics/kicad_files/8x8/8x8.kicad_pcb`。
    *   *操作技巧*: 按 `Alt + 3` 可以在 KiCad 中直接查看 PCB 的 3D 效果图。

### 第二步：修改模型 (2.2)
1.  **参数化修改 (Fusion 360)**: 找到底部的 **时间轴 (Timeline)**。如果你想改某个孔的大小，右键点击对应的“草图 (Sketch)”，选择 `Edit Sketch`。
2.  **联动修改**: 如果你改变了 PCB 的尺寸，你必须同步在 Fusion 360 中导入 PCB 的 3D 模型（在 KiCad 中导出为 `.step`），以确保外壳孔位依然匹配。

### 第三步：联系厂商生产 (2.3)
当你准备好文件后，如何跟加工厂沟通？

#### A. PCB 生产与 SMT 贴片 (找嘉立创等厂商)
*   **推荐导出流程 (KiCad 一键导出)**:
    1.  **安装插件**: 在 KiCad 主界面的 `Plugin and Content Manager` 中安装 **Fabrication Toolkit**。
    2.  **一键生成**: 打开 `.kicad_pcb` 文件，点击工具栏插件图标 -> `Generate`。
    3.  **获取文件**: 插件会在项目下生成 `production/` 文件夹，包含：
        *   `*.zip`: **Gerber 文件**（裸板生产用）。
        *   `bom.csv`: **物料清单**（SMT 贴片用）。
        *   `positions.csv`: **坐标文件**（SMT 贴片用，即 CPL/POS）。
*   **核心生产参数**: 
    *   **层数 (Layers)**: 2层。
    *   **板厚 (Thickness)**: 1.6mm。
    *   **阻焊颜色 (Solder Mask)**: 强烈建议选**白色**（漫反射 LED 灯光，视觉效果更均匀）。
    *   **表面工艺**: 有铅/无铅喷锡或沉金均可。

#### B. 3D 打印 (找网上的打印服务)
*   **术语**: “我要打印这个零件，格式是 **STL** 或 **STEP**，材料用 **PETG** 或 **PLA**。”
*   **核心参数**: 
    *   **填充率 (Infill)**: 15%-20% 即可，受力件建议 40% 以上。
    *   **层高 (Layer Height)**: 0.2mm 是常规精度，0.1mm 是高精度。

#### C. CNC / 激光切割 (处理木材或亚克力)
*   **术语**: “请按照这个 **DXF** 文件进行**激光切割**（或 **CNC 铣削**），材料用 **5mm 厚的胡桃木板**（或亚克力）。”
*   **核心参数**: 
    *   **切割 vs 雕刻**: 告诉师傅哪些线条是“切断”，哪些是“浅层雕刻”（如棋盘的网格线）。
    *   **比例单位**: 务必强调“单位是 **毫米 (mm)**”，防止厂商导入时比例缩放错误。

