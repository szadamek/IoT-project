import pandas as pd
import json
import requests
import paho.mqtt.client as mqtt
from flask import Flask, request
import threading
import time

df1 = pd.read_excel(r'files\final_grades.xlsx', sheet_name='first_time')
titles = []
for col in df1.columns:
    titles.append(col)
list_t = df1.values.tolist()

app = Flask("__main__")
change_ = False


def send(data, type_of_send, address, frequency, owned_ip, file_name='test.txt'):
    parameters = {'message': json.dumps(data), 'ip': owned_ip, 'file': file_name, 'type': type_of_send}
    if type_of_send == 'http':
        request = requests.post(address, params=parameters)
        requests.post("http://127.0.0.1:7000/aggregate/2", json=json.dumps(data))
        time.sleep(frequency)
        print(f"Wysłano: {data}")
    else:
        topic = 'testowy1'
        client = mqtt.Client('P1')
        client.connect(address)
        client.publish(topic, file_name)
        time.sleep(frequency)
        print(f"Wysłano: {data}")


@app.route('/change', methods=['POST'])
def get_config():
    data = request.json
    with open("config2.json", "w") as file_t:
        file_t.write(json.dumps(data))
    global change_
    change_ = True
    return ""


def send_():
    file = open("config2.json")
    read = json.load(file)
    file.close()
    for i in list_t:
        global change_
        if change_:
            file = open("config2.json")
            read = json.load(file)
            file.close()
        if read['change'] == "start":
            send(i, read['type_of_send'], read['address'], int(read['frequency']), read['ip'], read['file_name'])
        else:
            print("Wysyłanie zatrzymane.")
            while True:
                if change_:
                    file = open("config2.json")
                    read = json.load(file)
                    file.close()
                    if read['change'] == "start":
                        break
                time.sleep(1)


if __name__ == "__main__":
    t1 = threading.Thread(target=send_)
    t1.start()
    app.run(debug=False, port=8001)
