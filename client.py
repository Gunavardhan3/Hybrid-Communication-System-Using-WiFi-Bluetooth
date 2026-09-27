import socket
import subprocess
import time
import bluetooth
from datetime import datetime

ip = "10.215.41.186"
wp = 5000
bm = "D8:3A:DD:0E:03:BB"
bp = 1

ws = None
bs = None
busy = False

def wcon():
    global ws
    while True:
        try:
            ws = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            ws.connect((ip, wp))
            print("[WiFi] connected")
            return
        except:
            print("[WiFi] retry")
            time.sleep(2)

def bcon():
    global bs
    try:
        if bs:
            try:
                bs.close()
            except:
                pass
            bs = None

        print("[BT] connecting")
        s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        s.connect((bm, bp))
        bs = s
        print("[BT] connected")
    except Exception as e:
        bs = None
        print("[BT] connect fail:", e)

def brcon():
    global busy
    if busy:
        return
    busy = True
    try:
        print("[BT] reconnect")
        bcon()
    finally:
        busy = False

def rssi(m):
    try:
        o = subprocess.check_output(
            f"hcitool rssi {m}",
            shell=True,
            stderr=subprocess.DEVNULL
        ).decode().strip()

        v = o.split(":")[-1].strip()
        if v.startswith("0x"):
            v = int(v, 16)
            if v > 127:
                v -= 256
        else:
            v = int(v)
        return v
    except:
        return -100

def sw(m):
    global ws
    try:
        ws.sendall(m.encode())
    except:
        print("[WiFi] send fail")
        wcon()

def sb(m):
    global bs
    try:
        if bs is None:
            bcon()
        if bs is None:
            return
        bs.sendall((m + "\n").encode())
    except Exception as e:
        print("[BT] send fail:", e)
        brcon()

wcon()
bcon()

th = -60
tl = -75
mode = "wifi"

print("\n=== Hybrid client started ===")

while True:
    x = input("\nEnter message: ")
    rs = rssi(bm)

    if rs == -100:
        mode = "wifi"
    elif rs > th:
        mode = "bt"
    elif rs < tl:
        mode = "wifi"

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    m = f"[{ts}] {x} | via {mode} | RSSI={rs}"

    if mode == "bt":
        sb(m)
    else:
        sw(m)

    print("[TX]", m)