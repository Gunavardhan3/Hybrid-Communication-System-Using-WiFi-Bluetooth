import socket
import threading
import time
import bluetooth

wp = 5000
bp = 1

def wi():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", wp))
    s.listen(5)
    print("[WiFi] listening")

    while True:
        c, a = s.accept()
        print("[WiFi] connected:", a)
        threading.Thread(target=wh, args=(c,), daemon=True).start()

def wh(c):
    try:
        while True:
            d = c.recv(1024)
            if not d:
                break
            print("[WiFi RX]", d.decode(errors="ignore"))
    except:
        pass
    finally:
        try:
            c.close()
        except:
            pass
        print("[WiFi] client closed")

def bh(c):
    try:
        while True:
            d = c.recv(1024)
            if not d:
                break
            print("[BT RX]", d.decode(errors="ignore"))
    except:
        pass
    finally:
        try:
            c.close()
        except:
            pass
        print("[BT] client closed")

def bt():
    while True:
        s = None
        c = None
        try:
            s = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            s.bind(("", bp))
            s.listen(1)

            bluetooth.advertise_service(
                s,
                "HybridSrv",
                service_classes=[bluetooth.SERIAL_PORT_CLASS],
                profiles=[bluetooth.SERIAL_PORT_PROFILE],
            )

            print("[BT] waiting")
            c, a = s.accept()
            print("[BT] connected:", a)
            bh(c)

        except Exception as e:
            print("[BT] error:", e)

        finally:
            try:
                if c:
                    c.close()
            except:
                pass
            try:
                if s:
                    s.close()
            except:
                pass

        print("[BT] restart in 2s")
        time.sleep(2)

if __name__ == "__main__":
    threading.Thread(target=wi, daemon=True).start()
    threading.Thread(target=bt, daemon=True).start()

    print("=== Hybrid server running ===")
    while True:
        time.sleep(1)