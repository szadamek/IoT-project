import paho.mqtt.client as mqtt
import requests
import time
import json


def send(data, type_of_send, address, frequency, owned_ip, file_name='test.txt'):
    parameters = {'message': json.dumps(data), 'ip': owned_ip, 'file': file_name, 'type': type_of_send}
    if type_of_send == 'http':
        request2 = requests.post("http://127.0.0.1:9000/get_msg", params=parameters)
        request = requests.post(address, params=parameters)
        time.sleep(frequency)
        print(f"Wysłano: {data}")
    else:
        topic = 'testowy1'
        client = mqtt.Client('P1')
        client.connect(address)
        request2 = requests.post("http://127.0.0.1:9000/get_msg", params=parameters)
        client.publish(topic, file_name)
        time.sleep(frequency)
        print(f"Wysłano: {data}")
