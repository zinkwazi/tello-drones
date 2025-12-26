# Ryze / DJI Tello SDK Command Reference

This document is a practical reference for controlling **Tello** and **Tello EDU** drones using the official SDK over UDP.

It includes:
- A command reference
- Example command sequences (with code blocks)
- A full Python demo script showing common features
- Notes on controlling **multiple drones** from one computer

---

## Quick Start

### Network basics
- Connect your computer to the drone’s Wi‑Fi (default SSID often looks like `TELLO-XXXXXX`)
- The drone listens for SDK commands on:
  - **IP** `192.168.10.1`
  - **UDP port** `8889`

### Minimal “hello” test
Send `command` to enter SDK mode.

```python
import socket, time

TELLO_ADDR = ("192.168.10.1", 8889)

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(("", 9000))

sock.sendto(b"command", TELLO_ADDR)
time.sleep(1)
sock.close()
```

---

## SDK Mode

You must enter SDK mode before issuing flight commands.

| Command | Meaning |
|---|---|
| `command` | Enter SDK mode |

Example:
```text
command
```

Expected response: `ok` or `error`

---

## Takeoff, Landing, Emergency

| Command | Meaning |
|---|---|
| `takeoff` | Take off and hover |
| `land` | Land |
| `emergency` | Immediately stop motors (hard stop) |

Example:
```text
command
takeoff
land
```

---

## Movement Commands

All distances are **centimeters**. Typical range: **20–500**.

| Command | Meaning |
|---|---|
| `up x` | Move up |
| `down x` | Move down |
| `left x` | Move left |
| `right x` | Move right |
| `forward x` | Move forward |
| `back x` | Move backward |

Example:
```text
command
takeoff
up 50
forward 100
back 100
land
```

---

## Rotation

Angles are **degrees**. Typical range: **1–360**.

| Command | Meaning |
|---|---|
| `cw x` | Rotate clockwise |
| `ccw x` | Rotate counter‑clockwise |

Example:
```text
cw 180
```

---

## Speed Control

Speed is **cm/s**. Typical range: **10–100**.

| Command | Meaning |
|---|---|
| `speed x` | Set speed |

Example:
```text
speed 50
```

---

## Flips

Flips are fun but require:
- Adequate altitude
- Clear space (no obstacles)
- Good battery

| Command | Meaning |
|---|---|
| `flip l` | Flip left |
| `flip r` | Flip right |
| `flip f` | Flip forward |
| `flip b` | Flip backward |

Example:
```text
command
takeoff
up 80
flip f
land
```

---

## Telemetry Queries

These return a value (usually a number or a comma-separated set).

| Command | Returns |
|---|---|
| `battery?` | Battery percent |
| `height?` | Height in cm |
| `time?` | Flight time (seconds) |
| `speed?` | Current speed |
| `temp?` | Temperature |
| `wifi?` | Wi‑Fi signal |
| `attitude?` | pitch/roll/yaw |
| `acceleration?` | IMU acceleration |
| `baro?` | Barometer |
| `tof?` | Time-of-flight distance |

Example:
```text
battery?
attitude?
```

---

## Video Streaming

| Command | Meaning |
|---|---|
| `streamon` | Enable video stream |
| `streamoff` | Disable video stream |

The video stream is typically available at UDP port **11111**.

Example:
```text
command
streamon
```

---

## Advanced Flight (EDU features)

Some commands are **Tello EDU-only** (or firmware-dependent).

### Curve
Fly a curved path:

```text
curve x1 y1 z1 x2 y2 z2 speed
```

### Go (position move)
Move to a coordinate relative to current position:

```text
go x y z speed
```

---

## Joining a Tello to Your Wi‑Fi (and controlling multiple drones)

### Important reality check
- **Standard Tello**: typically creates its own Wi‑Fi and does **not** support joining your SSID directly.
- **Tello EDU**: may support “station mode” and can join an existing SSID.

### Tello EDU station mode command
While connected to the Tello’s Wi‑Fi:

```text
command
ap <ssid> <password>
```

Example:
```text
command
ap egg thewifipassword
```

If supported, the drone will drop its Wi‑Fi and attempt to join your SSID (2.4 GHz recommended; WPA2 recommended).

### Two drones on one Wi‑Fi
If you have **two Tello EDU** drones and both can join the same SSID:
- Put both into station mode
- Each should receive a unique IP from DHCP
- You then send commands to each drone’s IP (UDP/8889) using separate sockets or separate target addresses

Practical notes:
- You’ll need a way to discover each drone’s IP (router DHCP lease table is the easiest).
- Each drone is still controlled with the same command set, but the destination IP changes.

### If you have standard Tellos
A common workaround is a **travel router / Wi‑Fi bridge** setup:
- Your laptop stays on your main Wi‑Fi
- The bridge routes traffic to each Tello’s 192.168.10.0/24 network
- This is networking-heavy but reliable once configured

---

## Full Python Demo Script

This script:
- Enters SDK mode
- Queries telemetry (battery)
- Sets speed
- Takes off, moves, rotates
- Attempts a flip (optional)
- Turns video stream on/off (optional)
- Lands safely
- Prints `ok` / `error` responses

Save as `tello_demo.py` and run while connected to the Tello’s Wi‑Fi.

```python
import socket
import time
from typing import Optional, Tuple

# Target IP/port for a stock Tello while you are connected to its Wi‑Fi
TELLO_IP = "192.168.10.1"
TELLO_PORT = 8889
TELLO_ADDR: Tuple[str, int] = (TELLO_IP, TELLO_PORT)

# Any free local UDP port on your computer (used to receive replies)
LOCAL_UDP_PORT = 9000
RECV_BUFSZ = 1024

def send(sock: socket.socket, cmd: str) -> None:
    print(f">>> {cmd}")
    sock.sendto(cmd.encode("utf-8"), TELLO_ADDR)

def recv(sock: socket.socket, timeout: float = 5.0) -> Optional[str]:
    sock.settimeout(timeout)
    try:
        data, _ = sock.recvfrom(RECV_BUFSZ)
        msg = data.decode("utf-8", errors="ignore").strip()
        print(f"<<< {msg}")
        return msg
    except socket.timeout:
        print("<<< (no response)")
        return None

def cmd(sock: socket.socket, command: str, timeout: float = 5.0, post_delay: float = 0.3) -> Optional[str]:
    """
    Send a command and wait for a response.
    Increase timeout for long moves.
    """
    send(sock, command)
    resp = recv(sock, timeout=timeout)
    time.sleep(post_delay)
    return resp

def require_ok(resp: Optional[str], context: str) -> None:
    if resp != "ok":
        raise RuntimeError(f"{context} failed (response={resp!r}).")

def main() -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", LOCAL_UDP_PORT))

    try:
        # 1) Enter SDK mode
        require_ok(cmd(sock, "command", timeout=3), "enter SDK mode")

        # 2) Telemetry example
        batt = cmd(sock, "battery?", timeout=3)
        print(f"Battery: {batt}%")

        # 3) Set speed (cm/s)
        require_ok(cmd(sock, "speed 50", timeout=3), "set speed")

        # 4) Optional: enable video stream (receiver listens on UDP/11111)
        # require_ok(cmd(sock, "streamon", timeout=3), "streamon")

        # 5) Takeoff and stabilize
        require_ok(cmd(sock, "takeoff", timeout=10, post_delay=1.0), "takeoff")

        # 6) Flight pattern
        require_ok(cmd(sock, "up 40", timeout=7), "up")
        require_ok(cmd(sock, "forward 100", timeout=10), "forward")
        require_ok(cmd(sock, "cw 180", timeout=7), "cw 180")
        require_ok(cmd(sock, "forward 100", timeout=10), "forward (return)")

        # 7) Optional: flip (only if you have space and altitude)
        # require_ok(cmd(sock, "up 40", timeout=7), "up before flip")
        # require_ok(cmd(sock, "flip f", timeout=10, post_delay=1.0), "flip f")

        # 8) Land
        require_ok(cmd(sock, "land", timeout=10, post_delay=1.0), "land")

        # 9) Optional: disable stream
        # require_ok(cmd(sock, "streamoff", timeout=3), "streamoff")

        print("Done.")

    finally:
        sock.close()

if __name__ == "__main__":
    main()
```

---

## Extra “Cool Stuff” People Commonly Do

- Indoor flight “macros” (repeatable command sequences)
- Timed choreography (multiple drones) using scheduled command dispatch
- Vision tracking with OpenCV (read video stream and adjust commands)
- Simple “follow me” logic using marker detection (ArUco tags)
- Automated battery/health checks before flights
- Logging and replay of command sequences for consistent demos

---

## Safety Notes

- Fly at low speed indoors
- Give generous delays between commands
- Flips need clear space
- Use `emergency` only if you must (motors stop immediately)

---

## Troubleshooting

### No response
- You are not connected to the Tello Wi‑Fi
- You didn’t send `command` first
- Local UDP port is blocked by firewall

### `error`
- Command out of range (distance/speed)
- Next command sent too soon
- Drone can’t complete movement due to obstacle/low battery
