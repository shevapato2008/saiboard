# Product Guidelines / 产品指南

## Core Principles / 核心原则
- **Harmonious Tech Integration / 科技与传统的融合:** The physical board remains the center of the experience. AI and electronics should enhance, not overpower, the traditional game of Go. (棋盘本身仍是核心。AI与电子设备应起到增强作用，而非喧宾夺主。)
- **Educational Empowerment / 教育赋能:** Design for learning. Feedback (LEDs and UI) should be intuitive for all ages, especially children. (为学习而设计。LED灯光和界面反馈应直观，适合各年龄段，尤其是儿童。)
- **Configurable Feedback / 可自定义反馈:** Lighting (brightness, color, mode) and AI intensity must be adjustable. (灯光亮度、颜色、模式以及AI强度必须可调。)
- **Production-Ready Documentation / 生产就绪文档:** Clear instructions and assets for manufacturing. (提供清晰的制造说明和设计资产。)

## Manufacturing & Sourcing Guide / 制造与采购指南
- **Woodwork (The Board) / 木工 (棋盘):**
  - **Files / 文件:** `.f3d` (Fusion 360) / `.dxf` in `board/cnc_files/`.
  - **Keywords / 关键词:** CNC木材加工 (CNC Wood Machining), 激光切割 (Laser Cutting), 实木棋盘定制 (Solid Wood Go Board Customization).
- **PCB Fabrication / PCB 线路板制造:**
  - **Files / 文件:** Gerber files in `electronics/kicad_files/*/gerbers/`.
  - **Keywords / 关键词:** PCB打样 (PCB Prototyping), SMT贴片 (SMT Assembly), 嘉立创 (JLC), 捷配 (PCBWay).
- **3D Printing / 3D 打印:**
  - **Files / 文件:** `.f3d` / `.gcode` in `electronics/3d_prints/` & `stones/3d_prints/`.
  - **Keywords / 关键词:** 3D打印服务 (3D Printing Service), 光敏树脂 (Resin), PETG/PLA打印.
- **Electronic Components / 电子元器件:**
  - **Keywords / 关键词:** AH49E霍尔传感器 (AH49E Hall Sensor), SK6812 3535幻彩灯珠 (SK6812 3535 RGB LED), ESP32-S3开发板 (ESP32-S3 Development Board), 强磁围棋子 (Magnetic Go Stones).

## Development & Assembly / 开发与组装
- **Hardware Bridge / 硬件桥接:** ESP32-S3 (JSON over TCP, Port 3333).
- **macOS Workflow / macOS 开发流程:** ESP-IDF for firmware, Docker Compose for backend microservices. (使用 ESP-IDF 开发固件，Docker Compose 运行后端微服务。)
- **Design Tools / 设计工具:** Autodesk Fusion 360 (`.f3d`), KiCad (`.kicad_pcb`).

## Iterative Strategy / 迭代策略
- **Phase 1 (Stability):** Maintain existing backend and Flutter interface. (保持现有后端和 Flutter 界面稳定。)
- **Phase 2 (Evolution):** Transition to a custom Web GUI. (逐步过渡到自研 Web GUI。)
