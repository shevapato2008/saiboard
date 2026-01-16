# Tech Stack

## Hardware & Firmware
- **Controller:** ESP32-S3 (managing Hall sensor matrix and SK6812 LEDs)
- **AI Inference:** **Rockchip RK3588** (deployed for KataGo and model prediction services)
- **Firmware Framework:** ESP-IDF (C/C++)
- **Sensors:** AH49E Hall Effect Sensors (19x19 matrix)
- **Visuals:** SK6812 RGB LEDs
- **Protocols:** JSON over TCP (Port 3333)

## Backend Services (Python)
- **Service Orchestration:** Docker Compose
- **Message Broker:** Redis
- **Core Logic:** Python 3.x
- **AI Engine:** KataGo (running on RK3588)
- **Key Libraries:** `redis`, `numpy`, `websockets`, `aioredis`

## Frontend (Web)
- **Current Framework:** Flutter (Web)
- **Future Target:** Custom Web GUI (TypeScript/React or similar)
- **Communication:** WebSockets (Port 7654)

## Design & Manufacturing
- **Mechanical/CAD:** Autodesk Fusion 360 (`.f3d`)
- **Electronics/EDA:** KiCad (`.kicad_pcb`, `.kicad_sch`)
- **Sourcing:** Gerber files for PCB, DXF for CNC
