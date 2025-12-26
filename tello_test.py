import socket
import time

TELLO_IP = "192.168.10.1"
TELLO_PORT = 8889
ADDR = (TELLO_IP, TELLO_PORT)

def send(sock, cmd, delay=0.5):
    print(">>>", cmd)
    sock.sendto(cmd.encode("utf-8"), ADDR)
    time.sleep(delay)

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("", 9000))  # local port, arbitrary but required

    try:
        # Put Tello in SDK mode
        send(sock, "command", 1)

        # Fast mode (cm/s, valid 10–100)
        send(sock, "speed 50", 3)

        # Take off
        send(sock, "takeoff", 4)

        # Bump up a bit so total height is around 1.5 m indoors
        send(sock, "up 40", 3)   # go up an extra 50 cm

        # Forward 500 cm
        send(sock, "forward 100", 4)

        # Turn around (180 degrees)
        send(sock, "cw 180", 5)
        
        # Fly back 500 cm
        send(sock, "forward 100", 7)

        # Land
        send(sock, "land", 3)

    finally:
        sock.close()

if __name__ == "__main__":
    main()

