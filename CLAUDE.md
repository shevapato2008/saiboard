# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Saiboard is an open-source, AI-enhanced physical Go (围棋) board. A wooden board embeds 361 Hall effect sensors to detect magnetic stones and 361 SK6812 LEDs for visual feedback. An ESP32-S3 microcontroller manages hardware I/O, a Raspberry Pi (or RK3588) runs backend microservices and KataGo AI, and a Flutter web app provides the UI.

## Architecture

Three-tier system connected over a local WiFi network created by the ESP32:

```
Flutter Web UI (port 8000)
    ↕ WebSocket (port 7654)
Backend microservices (Docker on Pi @ 192.168.4.5)
    ├─ outside: WebSocket ↔ Redis bridge
    ├─ game:    Game state machine, move validation, coordinator
    ├─ katago:  KataGo AI analysis wrapper
    ├─ board:   Hardware interface (TCP client)
    └─ redis:   Pub/Sub message broker
    ↕ TCP JSON (port 3333)
ESP32-S3 firmware (AP @ 192.168.4.1)
    ├─ 19×19 Hall sensor matrix (multiplexed via 74HC4052/74HCT138)
    ├─ 361 SK6812 LEDs
    └─ Capacitive touch detection
```

**Redis channels:** `board_in`, `board_out`, `katago_in`, `katago_out`, `outside`, `game`.

**Key entry points:**
- `software/backend/game/play.py` — game state machine and service coordination
- `software/esp32s3/main/main.c` — firmware: sensors, LEDs, WiFi AP, TCP server
- `software/flutter/saiboard/lib/main.dart` — Flutter app entry and WebSocket handling

## Build & Run Commands

### Backend (Docker)
```bash
cd software/backend
docker compose build
docker compose up        # starts redis + all 4 services
docker compose down
```
The `katago` service uses `Dockerfile_rasp` for ARM64 (Raspberry Pi / RK3588).

### Flutter Frontend
```bash
cd software/flutter/saiboard
flutter pub get
flutter run -d web-server --web-port 8000          # local dev
flutter build web --web-renderer canvaskit --release # production build
```

### ESP32-S3 Firmware
Requires [ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/get-started/).
```bash
cd software/esp32s3
idf.py set-target esp32s3
idf.py build
idf.py flash monitor
```

### Deployment to Raspberry Pi
```bash
# Flutter
scp -r software/flutter/saiboard/build/web/* rashid@saiboardrasp.local:/home/rashid/flutter

# Backend
scp -r software/backend/* rashid@saiboardrasp.local:/home/rashid/backend
# Then SSH in, docker compose build && docker compose up
```

## Testing

No automated test suite exists yet. Validate changes manually:
- Backend: `docker compose up` and verify service interactions via Redis
- Frontend: load web UI and test board/socket interactions
- Hardware: use `software/esp32s3/test_basic_components.ipynb` for component checks

## Coding Conventions

- **Python** (`software/backend/`): 4-space indent, snake_case, keep `main.py` entrypoints minimal
- **Dart** (`software/flutter/saiboard/`): Flutter conventions, UpperCamelCase widgets, lowerCamelCase members. Linting via `flutter_lints` (see `analysis_options.yaml`)
- **C** (`software/esp32s3/`): ESP-IDF conventions
- Match existing filename patterns (e.g., `analysis_page.dart`, `game_record.py`)

## Commit Messages

Format: `<type>(<scope>): <description>` — types: feat, fix, docs, style, refactor, test, chore.

Conductor/planning commits use: `conductor(plan): ...`

## Hardware Design Files

- **PCB (KiCad):** `electronics/kicad_files/` — board types: `8x8`, `11x3`, `3x8`, `8x3` (segments that tile into the full 19×19)
- **Mechanical (Fusion 360):** `board/cnc_files/` (`.f3d`, `.dxf`), `electronics/3d_prints/`, `stones/3d_prints/`
- **PCB production:** export Gerber via KiCad Fabrication Toolkit plugin → `production/` folder with `.zip`, `bom.csv`, `positions.csv`. Target: 2-layer, 1.6mm, white solder mask.

## Project Management

The `conductor/` directory contains project planning and guidelines:
- `workflow.md` — TDD workflow and task lifecycle
- `tech-stack.md` — authoritative tech stack (update before changing dependencies)
- `product-guidelines.md` — core principles (bilingual CN/EN)
- `code_styleguides/` — Python and Dart style guides

## Key Hardware Parameters

Defined in `software/backend/board/main.py`:
- Board size: 19×19
- Hall sensor thresholds: white=40, black=-40, touch=3200
- Boot-up calibration rounds: 20

## Network Configuration

| Device | IP | Port | Protocol |
|---|---|---|---|
| ESP32-S3 (WiFi AP) | 192.168.4.1 | 3333 | TCP/JSON |
| Raspberry Pi | 192.168.4.5 | 7654 | WebSocket |
| Web UI | 192.168.4.5 | 8000 | HTTP |
| Redis | localhost | 6379 | Redis |
