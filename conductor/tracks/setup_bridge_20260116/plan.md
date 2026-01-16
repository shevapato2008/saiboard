# Implementation Plan: setup_bridge_20260116

## Phase 1: Environment Readiness [checkpoint: 5595990]
- [x] Task: Install and configure ESP-IDF on macOS
    - [x] Verify `idf.py --version`
- [x] Task: Set up Docker and Docker Compose
    - [x] Verify `docker compose version`
- [x] Task: Configure Python Virtual Environment for local scripts (using conda environment `py311_esp32s3`)
- [x] Task: Conductor - User Manual Verification 'Phase 1: Environment Readiness' (Protocol in workflow.md)

## Phase 2: Firmware & Communication
- [ ] Task: Flash base Wi-Fi/TCP server firmware to ESP32-S3
- [ ] Task: Verify TCP connection from macOS to ESP32-S3 (Port 3333)
- [ ] Task: Implement/Verify JSON handshake protocol
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Firmware & Communication' (Protocol in workflow.md)

## Phase 3: Hardware Loopback Verification
- [ ] Task: Verify Hall sensor matrix data stream
    - [ ] Run `software/esp32s3/test_basic_components.ipynb` logic
- [ ] Task: Verify LED strip control commands
- [ ] Task: Integration test: Board service (Backend) <-> ESP32-S3 Firmware
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Hardware Loopback Verification' (Protocol in workflow.md)
