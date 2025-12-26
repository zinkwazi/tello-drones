import socket
import time

TELLO_IP = "192.168.10.1"
TELLO_PORT = 8889
ADDR = (TELLO_IP, TELLO_PORT)

def send(sock, cmd):
    print(">>>", cmd)
    sock.sendto(cmd.encode("utf-8"), ADDR)

def recv(sock, timeout=5):
    sock.settimeout(timeout)
    try:
        data, _ = sock.recvfrom(1024)
        print("<<<", data.decode("utf-8", errors="ignore"))
        return data.decode("utf-8", errors="ignore").strip()
    except socket.timeout:
        print("<<< (no response)")
        return None

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", 9000))

    try:
        send(sock, "command")
        recv(sock, 3)

        send(sock, "ap egg thewifipassword")
        resp = recv(sock, 8)

        if resp == "ok":
            print("Sent OK. Tello should reboot/drop Wi-Fi and attempt to join egg.")
        elif resp == "error":
            print("Tello replied ERROR. This usually means your model/firmware doesn't support station mode.")
        else:
            print("No response. Either not in SDK mode, not on Tello Wi-Fi, or command unsupported.")
    finally:
        sock.close()

if __name__ == "__main__":
    main()

