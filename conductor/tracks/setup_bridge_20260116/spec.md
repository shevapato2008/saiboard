# Specification: setup_bridge_20260116

## Goal
Establish a reliable development and testing environment on macOS to verify the core hardware-software bridge of the Saiboard project.

## Scope
- **Environment Setup:** Install and configure ESP-IDF, Docker, and Python dependencies on macOS.
- **Hardware Communication:** Verify the ESP32-S3 can connect to Wi-Fi and communicate with the backend.
- **Sensor Verification:** Run basic tests to ensure Hall effect sensor data is correctly received by the backend.
- **LED Verification:** Verify the backend can send commands to the ESP32-S3 to control the SK6812 LEDs.

## Success Criteria
- ESP-IDF is functional and can flash the ESP32-S3.
- Backend microservices (board, game, outside) are running in Docker.
- A "ping-pong" test between the backend and firmware (TCP Port 3333) succeeds.
- Real-time sensor data is visible in the backend logs upon stone placement.
