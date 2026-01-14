# Repository Guidelines

## Project Structure & Module Organization
- `board/` contains CNC files and build notes for the physical board.
- `electronics/` covers wiring, PCB, and hardware documentation.
- `stones/` documents stone fabrication.
- `software/` holds firmware and software:
  - `software/esp32s3/` ESP32-S3 firmware for Wi-Fi, sensors, and LEDs.
  - `software/backend/` Python services plus `docker-compose.yml` (board/game/katago/outside).
  - `software/flutter/saiboard/` Flutter web UI.
- `pics/` stores images used in docs and UI previews.

## Build, Test, and Development Commands
- Backend stack:
  - `cd software/backend`
  - `docker compose build` builds the containers.
  - `docker compose up` starts Redis + services; `docker compose down` stops them.
- Flutter web UI:
  - `cd software/flutter/saiboard`
  - `flutter clean` removes old build artifacts.
  - `flutter build web --web-renderer canvaskit --release` outputs `build/web`.
  - `python -m http.server 8000` serves the web build (matches the Pi setup in `software/readme.md`).
- Firmware: follow ESP-IDF setup links in `software/esp32s3/README.md`.

## Coding Style & Naming Conventions
- Python (`software/backend`): 4-space indentation, snake_case modules/functions; keep entrypoints like `main.py` minimal.
- Dart (`software/flutter/saiboard`): Flutter conventions (UpperCamelCase widgets, lowerCamelCase members); linting via `flutter_lints` in `software/flutter/saiboard/analysis_options.yaml`.
- Match existing filenames such as `analysis_page.dart` or `game_record.py`.

## Testing Guidelines
- No automated test suite is defined yet; validate changes manually.
- Suggested checks: bring up the backend stack, load the web UI, and verify board/socket interactions.
- Hardware sanity checks can use `software/esp32s3/test_basic_components.ipynb`.

## Commit & Pull Request Guidelines
- Commit messages are short and imperative, sometimes with issue refs (e.g., `#74 #75`); follow that pattern.
- PRs should include a clear description, affected areas (hardware/firmware/backend/UI), and validation notes; add photos or screenshots for UI or physical changes.
