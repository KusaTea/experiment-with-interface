import json
import select
import socket
import threading
import time


HOST = "127.0.0.1"

BINARY_PORT = 10000
JSON_PORT = 10001

BINARY_SEND_INTERVAL = 0.001
JSON_SEND_INTERVAL = 0.0054


SENSO_DATA = {
    "src": "ac:4d:16:e8:aa:e6",
    "version": "3.1",
    "name": "SensoDK3",
    "fullname": "SensoDK3",
    "type": "position",
    "data": {
        "type": "rh",
        "ts": "13422646181121",
        "palm": {
            "pos": [0.0, 0.0, 0.0],
            "spd": [0.0, 0.0, 0.0],
            "quat": [0.884455, 0.329943, -0.292625, 0.152471],
            "grv": [5.298, 7.298, 3.802],
            "lia": [1.521, 0.002, -0.142],
            "delta": 0.0054,
            "tilt": 0.517151
        },
        "gests": [
            0.6665,
            -0.64186,
            0.12614,
            0.68341,
            0.92981,
            1.30236,
            1.04984,
            -0.09156,
            -0.94088,
            0.25375
        ],
        "wrist": {
            "quat": [0.973286, 0.028098, -0.216899, 0.069852],
            "grv": [-5.452, 4.066, -7.089],
            "lia": [1.66, 0.174, -0.129],
            "delta": 0.0054,
            "tilt": 0.024396
        },
        "bones": [
            0.884455, 0.292625, 0.152471, -0.329943,
            0.95519, 0.23237, 0.06335, 0.17203,
            0.96284, 0.0811, -0.04685, -0.25333,
            0.97729, -0.07601, 0.0434, -0.19299,
            0.98309, -0.04186, 0.01129, -0.1779,
            0.97603, 0.02622, -0.00185, -0.21606,
            0.99753, 0.01666, -0.02492, -0.06352,
            0.97443, -0.03758, -0.03775, -0.21827,
            0.97927, 0.01228, -0.00199, -0.20216,
            0.99837, 0.04676, 0.00087, -0.0327,
            0.94328, -0.1203, -0.10149, -0.29231,
            0.92304, 0.03906, 0.00899, -0.38262,
            0.97796, 0.01383, 0.02937, -0.20627,
            0.9294, -0.12723, -0.13402, -0.31949,
            0.95395, 0.06005, -0.02929, -0.29243,
            0.98839, -0.0012, 0.04823, -0.1441
        ],
        "fingers": [
            {
                "ang": [0.011768, 0.308993],
                "quat": [0.9724, -0.1894, -0.0726, 0.1149],
                "q": [0.972446, 0.114942, 0.189395, 0.07257],
                "bend": 0.126,
                "quat2": [0.998012, 0.046804, 0.014733, -0.039561],
                "spd": 15.4344,
                "grv": [-7.151, -3.375, -5.968],
                "lia": [0.415, -0.199, -0.927],
                "grv2": [-7.127, -2.59, -6.581],
                "lia2": [-0.336, -0.659, 0.554]
            },
            {
                "ang": [0.683411, 0.047472],
                "quat": [0.939657, 0.334364, 0.026318, -0.067479],
                "spd": 7.7964,
                "grv": [-3.227, 8.49, -3.605],
                "lia": [-1.201, -0.696, 1.078]
            },
            {
                "ang": [0.929808, 0.010592],
                "quat": [0.890438, 0.449001, 0.058375, -0.045943],
                "spd": 8.5254,
                "grv": [-3.977, 8.653, -1.809],
                "lia": [-1.073, -1.296, 0.492]
            },
            {
                "ang": [1.302358, -0.013957],
                "quat": [0.779213, 0.605868, 0.140307, -0.077875],
                "spd": 9.7546,
                "grv": [-3.919, 9.575, -1.565],
                "lia": [-1.448, -1.075, 0.49]
            },
            {
                "ang": [1.049835, 0.024149],
                "quat": [0.862098, 0.499812, 0.046792, -0.06918],
                "spd": 15.673,
                "grv": [-1.825, 9.573, 0.417],
                "lia": [-1.384, -3.032, 0.765]
            }
        ],
        "m1": [-228, 190, -89],
        "h_rssi": -55,
        "h_gain": 15,
        "g_rssi": -51,
        "g_gain": 15
    }
}


def handle_binary_client(client_socket, address):
    print(f"[1000] client is connected: {address}")

    try:
        first_message = client_socket.recv(4096)

        if not first_message:
            print(f"[1000] client {address} has disconnected before launch")
            return

        print(
            f"[1000] A message was recieved"
            f"({len(first_message)} bytes): {first_message!r}"
        )

        print("[1000] Transfer was started")

        value = 0

        while True:
            readable, _, _ = select.select(
                [client_socket],
                [],
                [],
                0
            )

            if readable:
                second_message = client_socket.recv(4096)

                # recv() == b"" означает закрытие соединения
                if not second_message:
                    print(f"[1000] Client {address} disconnected")
                    break

                print(
                    f"[1000] Stop-message "
                    f"({len(second_message)} bytes): "
                    f"{second_message!r}"
                )

                print("[1000] Transfer is over")
                break

            client_socket.sendall(bytes([value]))

            value = (value + 1) % 256

            if BINARY_SEND_INTERVAL:
                time.sleep(BINARY_SEND_INTERVAL)

    except (
        ConnectionResetError,
        ConnectionAbortedError,
        BrokenPipeError
    ):
        print(f"[1000] Connection with {address} is lost")

    finally:
        client_socket.close()
        print(f"[1000] Connection with {address} is closed")


def binary_server():
    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as server_socket:

        server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        server_socket.bind((HOST, BINARY_PORT))
        server_socket.listen()

        print(
            f"[1000] Server is launched: "
            f"{HOST}:{BINARY_PORT}"
        )

        while True:
            client_socket, address = server_socket.accept()

            thread = threading.Thread(
                target=handle_binary_client,
                args=(client_socket, address),
                daemon=True
            )

            thread.start()


def handle_json_client(client_socket, address):

    print(f"[1001] Client is connected: {address}")

    message = (
        json.dumps(
            SENSO_DATA,
            ensure_ascii=False,
            separators=(",", ":")
        )
        + "\n"
    ).encode("utf-8")

    try:
        while True:
            client_socket.sendall(message)

            if JSON_SEND_INTERVAL:
                time.sleep(JSON_SEND_INTERVAL)

    except (
        ConnectionResetError,
        ConnectionAbortedError,
        BrokenPipeError
    ):
        pass

    finally:
        client_socket.close()
        print(f"[1001] Client {address} disconnected")


def json_server():

    with socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    ) as server_socket:

        server_socket.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        server_socket.bind((HOST, JSON_PORT))
        server_socket.listen()

        print(
            f"[1001] Server is launched: "
            f"{HOST}:{JSON_PORT}"
        )

        while True:
            client_socket, address = server_socket.accept()

            thread = threading.Thread(
                target=handle_json_client,
                args=(client_socket, address),
                daemon=True
            )

            thread.start()


def main():
    binary_thread = threading.Thread(
        target=binary_server,
        daemon=True
    )

    json_thread = threading.Thread(
        target=json_server,
        daemon=True
    )

    binary_thread.start()
    json_thread.start()

    print()
    print("Both servers are launched.")
    print(f"Binary: {HOST}:{BINARY_PORT}")
    print(f"JSON:   {HOST}:{JSON_PORT}")
    print("Ctrl+C to stop servers.")
    print()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping servers...")


if __name__ == "__main__":
    main()