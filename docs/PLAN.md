# Saiboard Construction Plan (RK3588 Edition)

This plan is tailored to your setup: **RK3588 (ARM64)**, **ESP32-S3**, and existing **KataGo** deployment.

## Phase 0: Network Topology & Address Plan
*Goal: Decide how RK3588, ESP32-S3, and the UI find each other before you wire or flash anything.*

Default (matches the repo):
- ESP32-S3 runs SoftAP `saiboard` at `192.168.4.1` (`software/esp32s3/components/wifi/wifi.c`).
- RK3588 connects to that AP and uses a static IP such as `192.168.4.5`.
- Backend `board` service connects to `192.168.4.1:3333` (`software/backend/board/main.py`).
- Flutter UI connects to `ws://192.168.4.5:7654` (`software/flutter/saiboard/lib/main.dart`).

If you switch ESP32 to Station Mode (home Wi-Fi):
- Update `software/esp32s3/components/wifi/wifi.c` to STA.
- Set static/DHCP-reserved IPs for both ESP32 and RK3588.
- Update `software/backend/board/main.py` with the ESP32 IP.
- Update the WebSocket URL in `software/flutter/saiboard/lib/main.dart`, then rebuild.

## Phase 1: Electronics & Firmware Prototype (The "Bench Test")
*Goal: Validate the software stack and basic hardware control before committing to the full build.*

### 1.0 Bench-Test Mode (8x8 LED Matrix)
If you are using the 8x8 LED matrix for early testing, create a temporary branch and adjust the firmware so indices stay within 0-63:
- In `software/esp32s3/main/main.c`, set `strip.length = 64`.
- Replace `_row_col_to_nr` with `return row * 8 + col;` and only send row/col in 0..7.
- Skip hall-sensor validation for now (the sensor scan is hard-coded for 19x19).

### 1.1 Firmware Setup (ESP32-S3)
You need to adapt the firmware to your specific hardware setup.
1.  **Install ESP-IDF:** Follow the standard [Espressif guide](https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/get-started/).
2.  **Pin Mapping (Critical):**
    *   Open `software/esp32s3/main/main.c`.
    *   Review the `#define` macros (lines 12-29). The code assumes specific GPIOs for the LED strip (`LED_PIN_AT_5`) and the multiplexer logic (`A0`..`A3`, `S0`..`S1`).
    *   **Action:** Update these GPIO numbers to match your actual wiring between the ESP32-S3 and your 8x8 LED matrix/sensor test setup.
3.  **Wi-Fi Configuration:**
    *   The default code (likely in `components/wifi`) sets up an Access Point (AP) named "saiboard".
    *   **Recommendation:** For development, it's often easier to switch this to **Station Mode** so both the RK3588 and ESP32 connect to your home Wi-Fi. You will likely need to modify `components/wifi/wifi.c`.
4.  **Build & Flash:**
    ```bash
    cd software/esp32s3

    # 1. 目标芯片设置 (Chip Selection)
    # 目的：配置项目针对 ESP32-S3 芯片。
    # 作用：根据 S3 的架构和外设重新生成默认配置 (sdkconfig)。
    $ idf.py set-target esp32s3

    # 2. 项目构建 (Build)
    # 目的：编译代码并链接底层库。
    # 作用：生成最终的 .bin 固件文件。后续代码修改后只需执行此步。
    $ idf.py build

    # 3. 烧录与监控 (Flash & Monitor)
    # 目的：将固件写入芯片并开启串口日志查看。
    # 作用：'flash' 写入闪存，'monitor' 启动终端查看 ESP_LOGI 输出。
    # 提示：按 'Ctrl + ]' 退出监控模式。
    $ ls /dev/cu.*                                  
    /dev/cu.Bluetooth-Incoming-Port /dev/cu.debug-console           /dev/cu.usbmodem2101
    $ idf.py -p /dev/cu.usbmodem2101 flash monitor  # 请替换为您的实际端口
    ```

### 1.2 Validate with 8x8 Matrix
1.  Connect your 8x8 LED matrix to the defined LED pin.
    * Video Reference: [9.9合宙ESP32C3驱动WS2812灯珠，低成本灯带驱动板](https://www.bilibili.com/video/BV1824y1D7er/?vd_source=be274acb79d0df9850b3009e5244f7d3)
    * Video Reference: [【复刻】程序员的私人定制桌搭（esp32+点阵屏）](https://www.bilibili.com/video/BV1JbcJeUE7q/?vd_source=be274acb79d0df9850b3009e5244f7d3)
2.  Use `netcat` to test the TCP server (default port 3333):
    ```bash
    # Send a test JSON command to light up an LED (0-based row/col).
    # Use [0..7] if you enabled 8x8 bench mode, or [0..18] on the full board.
    echo '{"name":"led", "leds":[[3,3,255,0,0,0]]}' | nc <ESP32_IP> 3333
    ```
    执行结果类似
    ```bash
    $ echo '{"name":"sensor"}' | nc 192.168.4.1 3333
    {"hall":[[325,230,465,413,346,355,100,0],[279,302,459,392,337,351,164,0],[253,216,287,357,293,302,83,0],[293,232,371,341,287,311,158,0],[277,247,3
    91,340,291,284,77,0],[236,263,306,319,275,329,184,0],[279,279,463,405,359,379,267,0],[359,341,508,524,458,492,331,0]],"touch":17904}
    ```

## Phase 2: Backend Adaptation (RK3588)
*Goal: Run the control logic on your RK3588, utilizing your existing KataGo.*

### 2.1 Container Configuration
The provided `software/backend/docker-compose.yml` builds 5 services (`board`, `outside`, `game`, `katago`, `redis`). On RK3588 you must swap the x86_64 KataGo binary.

1.  **Edit `software/backend/docker-compose.yml`:**
    *   The default Dockerfile downloads the x64 KataGo zip and will not run on ARM64.
    *   **Option A (Container, CPU):** Switch to `software/backend/katago/Dockerfile_rasp` to build KataGo from source on ARM (Eigen, CPU-only).
    *   **Option B (Container, your binary):** Mount your RK3588-optimized `katago` + model into `/workspace/katago` and keep paths aligned with `software/backend/katago/main.py`.
    *   **Option C (Host, NPU):** Run `software/backend/katago/main.py` directly on the RK3588 and point it to your installed KataGo binary. If you do this, update its Redis host from `redis` to your actual Redis address (or run Redis on the host and adjust `docker-compose.yml` accordingly).
    *   **Reference:** KataGo paths are hardcoded in `software/backend/katago/main.py`.

2.  **Network Config:**
    *   Ensure the `board` service knows the IP address of your ESP32.
    *   `software/backend/board/main.py` defaults to `192.168.4.1` and port `3333`. Change it if you move away from the SoftAP topology.
    *   If you prefer not to edit code repeatedly, add an `ESP32_IP` environment variable and read it in Python.

3.  **Launch:**
    ```bash
    cd software/backend
    docker compose up --build
    ```

## Phase 3: Frontend (Flutter Web)
*Goal: Visualization interface.*

1.  **Build:**
    *   Install Flutter on your Mac (or the RK3588 if you prefer dev there).
    *   `cd software/flutter/saiboard`
    *   `flutter build web`
2.  **Deploy:**
    *   Copy the `build/web` folder to the RK3588.
    *   Serve it using any web server (Nginx, Python, etc.):
        ```bash
        cd build/web
        python3 -m http.server 8000
        ```
3.  **Connect:**
    *   **Crucial Config:** The WebSocket URL is hardcoded in `software/flutter/saiboard/lib/main.dart` (line 42).
    *   Change `'ws://192.168.4.5:7654'` to your RK3588's IP address (e.g., `'ws://192.168.1.100:7654'`).
    *   Rebuild with `flutter build web` after changing this.
    *   Open `http://<RK3588_IP>:8000` in a browser.

## Phase 4: Hardware Construction (The Physical Build)
*Goal: The full 19x19 board.*

### 4.1 PCBs (Required)
You cannot easily hand-wire 361 Hall sensors. You must order the PCBs.
1.  **Files:** `electronics/kicad_files/` contains folders for `11x3`, `3x8`, `8x3`, `8x8`.
2.  **Ordering:** Zip the `gerbers/` folder inside each of those directories and upload to a PCB manufacturer (JLCPCB, PCBWay, etc.).
3.  **Components:**
    *   **Hall Sensors:** 361x `AH49E` (Linear Hall Effect).
    *   **LEDs:** 361x `SK6812` (Side-emitting or standard 5050 depending on the PCB footprint, check carefully).
    *   **Multiplexers:** `74HC4052` and `74HCT138` (Quantities depend on the total board count).
4.  **Assembly:** Solder paste + Reflow oven (or hot plate) is highly recommended for this volume of components.

### 4.2 Frame
1.  **Top Plate:** Needs precise holes for the LEDs/Sensors.
    *   Use `board/cnc_files/top.dxf` if you have access to a CNC router.
    *   If not, you can try printing the `f3d` files in sections, but wood is preferred for the feel/aesthetic.
2.  **Veneer:** A 0.6mm wood veneer goes *over* the sensors/LEDs. The magnets must be strong enough to trigger the Hall sensors through this layer + the PCB distance. **Test this with your prototype before gluing!**

### 4.3 Stones
1.  **Magnets:** You need small neodymium magnets glued into the stones.
2.  **Polarity:** Ensure all stones have the same polarity facing down (so the Hall sensor reads consistently positive or negative values). Ideally, White and Black stones might use opposite polarities if the software supports it (for auto-color detection), but usually, the game logic tracks turns, and presence/absence is enough. The `AH49E` is linear, so it detects field strength.

### 4.4 Touch Plate & Mounting
Follow the touch plate and mounting steps in `electronics/README.md`, including copper foil, double-sided tape, and wiring to the ESP32 touch pin. The touch plate affects move detection thresholds, so build it before calibration.

## Phase 5: Calibration & Tuning
*Goal: Make sensor readings stable and aligned with your stones and veneer thickness.*

1.  **Hall Sensor Baseline:** With an empty board, run the backend and capture baseline readings (`software/backend/board/main.py` boot-up phase). Adjust `threshold_white` and `threshold_black` if stones are missed or false positives appear.
2.  **Touch Threshold:** Adjust `threshold_touch` and `touch_correct_factor` to avoid triggering moves while sliding stones.
3.  **End-to-End Check:** With the full stack running, place stones across corners/edges/center and verify LED highlighting + move detection.

## Summary Checklist
- [ ] Flash ESP32-S3 with adjusted pinout.
- [ ] Verify 8x8 matrix + 1 sensor works with `netcat` commands.
- [ ] Adapt Backend Docker to run on RK3588 and talk to ESP32 IP.
- [ ] Build & Serve Flutter Web App.
- [ ] Order PCBs.
- [ ] Assemble Frame & Stones.
