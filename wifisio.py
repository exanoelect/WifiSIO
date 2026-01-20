import socketio
import subprocess
import shlex

SERVER_URL = "http://127.0.0.1:5100"  # ganti jika server beda

sio = socketio.Client()

def run_cmd(cmd):
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20
        )
        return {
            "cmd": cmd,
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }
    except Exception as e:
        return {
            "cmd": cmd,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e)
        }

@sio.event
def connect():
    print("Connected to Socket.IO server")

@sio.event
def disconnect():
    print("Disconnected from server")

# 1️⃣ Event: wifi_list
@sio.on("wifi_list")
def handle_wifi_list(data=None):
    cmd = "nmcli device wifi list"
    result = run_cmd(cmd)
    sio.emit("wifi_list_result", result)

# 2️⃣ Event: wifi-del-con
# Data expected: "NAMA_WIFI"
@sio.on("wifi-del-con")
def handle_wifi_delete(name):
    if not name:
        sio.emit("wifi_del_result", {"error": "Nama WiFi kosong"})
        return

    cmd = f'nmcli connection delete "{name}"'
    result = run_cmd(cmd)
    sio.emit("wifi_del_result", result)

# 3️⃣ Event: wifi-con
# Data expected: "Nama_SSID, Password_wifi"
@sio.on("wifi-con")
def handle_wifi_connect(data):
    try:
        ssid, password = [x.strip() for x in data.split(",", 1)]
    except Exception:
        sio.emit("wifi_con_result", {"error": "Format harus: Nama_SSID, Password_wifi"})
        return

    cmd = f'nmcli device wifi connect "{ssid}" password "{password}"'
    result = run_cmd(cmd)
    sio.emit("wifi_con_result", result)

if __name__ == "__main__":
    sio.connect(SERVER_URL)
    sio.wait()

