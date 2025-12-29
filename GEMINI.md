# GEMINI.md - Saiboard Project Context

## Project Overview
Saiboard is an open-source, AI-enhanced physical Go board. It integrates traditional gameplay with modern technology using:
- **Hardware**: A wooden board with a grid of Hall effect sensors to detect magnetic Go stones and SK6812 LEDs for visual feedback (AI moves, analysis).
- **Firmware**: ESP32-S3 microcontroller managing sensors and LEDs, acting as a Wi-Fi Access Point and TCP server.
- **Backend**: A microservices architecture running in Docker (typically on a Raspberry Pi), using Redis for inter-process communication.
- **AI**: Integrated [KataGo](https://github.com/lightvector/KataGo) analysis engine.
- **Frontend**: A Flutter web application for game control and deep analysis visualization.

## Technical Architecture

### 1. Firmware (`software/esp32s3/`)
- **Framework**: ESP-IDF.
- **Role**: 
  - Creates a Wi-Fi network (AP mode).
  - Starts a TCP server on port `3333`.
  - Handles JSON requests for reading Hall sensors (19x19 grid) and controlling LEDs.
  - Monitors touch sensitivity to avoid sensor interference during move placement.

### 2. Backend (`software/backend/`)
Four main Python services communicating via **Redis**:
- **`board`**: TCP client to ESP32-S3. Translates raw sensor data into board states and sends LED commands.
- **`katago`**: Wraps the KataGo analysis engine, providing move suggestions and score estimates.
- **`game`**: Core logic. Manages game records, move validation, and coordinates between `board` and `katago`.
- **`outside`**: WebSocket server (port `7654`) providing an interface for the Flutter frontend.

### 3. Frontend (`software/flutter/saiboard/`)
- **Framework**: Flutter (Web).
- **Role**: User interface for starting games, reviewing moves, and visualizing AI analysis (win rates, score leads, ownership heatmaps).

## Development Guide

### Building and Running

#### ESP32 Firmware
Requires [ESP-IDF](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/get-started/index.html).
```bash
cd software/esp32s3
idf.py build
idf.py flash
```

#### Backend Services
Requires Docker and Docker Compose.
```bash
cd software/backend
# For Raspberry Pi, ensure the correct Dockerfile is used in katago/
docker compose build
docker compose up
```

#### Flutter Frontend
```bash
cd software/flutter/saiboard
flutter pub get
# To run locally:
flutter run -d web-server --web-port 8000
# To build for deployment:
flutter build web --web-renderer canvaskit --release
```

### Communication Protocols
- **ESP32 <-> Backend (`board` service)**: JSON over TCP (Port 3333).
- **Backend <-> Backend**: Redis Pub/Sub.
  - Channels: `board_in`, `board_out`, `katago_in`, `katago_out`, `outside`, `game`.
- **Backend (`outside` service) <-> Frontend**: JSON over WebSockets (Port 7654).

### Key Files
- `software/backend/docker-compose.yml`: Defines the backend microservices.
- `software/backend/game/play.py`: Main game state machine and coordination logic.
- `software/esp32s3/main/main.c`: Firmware entry point and sensor/LED drivers.
- `software/flutter/saiboard/lib/main.dart`: Frontend entry and WebSocket handling.

## Development Conventions
- **Microservices**: Keep logic decoupled. Hardware-specific code belongs in the `board` service or firmware. AI-specific code in `katago`.
- **State Management**: The `game` service is the source of truth for the current game state.
- **Hardware Safety**: When modifying firmware, be mindful of the multiplexing logic for the 361 Hall sensors to avoid ghosting or slow read cycles.
