import threading
import time
import requests
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

# Global variables
time_limit_reached = False
time_limited_devices = []
sending_active = False
ip_of_device = ""
frequency = 0
send_to_address = ""
file_name = ""
send_type = ""
change_setting = ""



@app.route("/home", methods=["POST", "GET"])
def home():
    return render_template("index.html")


@app.route("/on_off", methods=["POST", "GET"])
def on_off_status():
    global time_limit_reached
    # Read list of devices from file
    with open("generators.txt") as f:
        device_list = f.readlines()

    # Initialize device status list
    device_status = ["off"] * len(device_list)
    type_status = [" "] * len(device_list)

    # If time limit is reached, reset device status
    if time_limit_reached:
        device_status = ["off"] * len(device_list)
        time_limit_reached = False

    # Update status of time-limited devices
    for device_index in time_limited_devices:
        if device_index > 0:
            device_status[device_index - 1] = "on"
            type_status[device_index - 1] = send_type

    # Render template with device list and status
    return render_template("on_off.html", devices=device_list, status=device_status, type=type_status,
                           ids=[x for x in range(len(device_list))])


@app.route("/manage", methods=["POST", "GET"])
def manage_sending():
    global sending_active, ip_of_device, frequency, send_to_address, file_name, send_type, change_setting
    # Read list of devices from file
    with open("generators.txt") as f:
        device_list = f.readlines()

    if request.method == "POST":
        # Update global variables with form data
        ip_of_device = request.form["choose_ip"]
        frequency = int(request.form["frequency"])
        send_to_address = request.form["address"]
        file_name = request.form["file_name"] + ".txt"
        send_type = request.form["type"]
        change_setting = request.form["start_stop"]
        sending_active = True

    return render_template("manage.html", ips=device_list)


@app.route("/get_msg", methods=["POST"])
def update_time_limited_devices():
    global send_type
    # Get device information from request args
    device_info = request.args.to_dict()
    new_device = True

    # Read list of devices from file
    with open("generators.txt") as f:
        device_list = f.readlines()

    # Update send type
    send_type = device_info["type"]
    # Check if device is already in list
    for i, device in enumerate(device_list):
        if device == device_info["ip"] + "\n":
            new_device = False
            time_limited_devices.append(i + 1)
            break

    # If device is not in list, add it
    if new_device:
        with open("generators.txt", "a") as f:
            f.write(device_info["ip"] + "\n")
        time_limited_devices.append(len(device_list) + 1)

    return ""


def update_time_limit():
    global time_limit_reached, time_limited_devices
    while True:
        time.sleep(20)
        time_limit_reached = True
        time_limited_devices = [0] * len(time_limited_devices)


def send_data():
    global sending_active, ip_of_device, frequency, send_to_address, file_name, send_type, change_setting
    while True:
        time.sleep(5)
        if sending_active:
            device_ip = ip_of_device + "/change"
            data = {
                "type_of_send": send_type,
                "address": send_to_address,
                "frequency": frequency,
                "ip": ip_of_device,
                "file_name": file_name,
                "change": change_setting
            }
            requests.post(device_ip, json=data)
            sending_active = False


if __name__ == "__main__":
    # Start update and send threads
    update_thread = threading.Thread(target=update_time_limit)
    send_thread = threading.Thread(target=send_data)
    update_thread.start()
    send_thread.start()

    # Run Flask app
    app.run(debug=True, port=9000)
