from flask import Flask, render_template, request
from os import listdir
from os.path import isfile, join
from flask_mqtt import Mqtt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'files'
app.config['MQTT_BROKER_URL'] = 'test.mosquitto.org'
app.config['MQTT_KEEPALIVE'] = 100
topic = 'testowy1'

mqtt_client = Mqtt(app)


@app.route('/', methods=['GET', "POST"])
@app.route('/home', methods=['GET', "POST"])
def home():
    return render_template('index.html')


@app.route('/get_file', methods=['GET', 'POST'])
def get_message():
    arguments = request.args.to_dict()
    file_name = arguments['file']
    f = open("files/" + file_name, "a")
    f.write(arguments['message'] + "\n")
    f2 = open("generators.txt")
    tlines = f2.readlines()
    f2.close()
    p = True
    for i in tlines:
        if i == arguments['ip'] + "\n":
            p = False
    if p:
        f3 = open("generators.txt", "a")
        f3.write(arguments['ip'] + "\n")
    return render_template('index.html')


@app.route('/read_file', methods=['GET', 'POST'])
def read_message():
    file, info, my_path = 'test1.txt', 'Nie wybrano istniejącego pliku, wczytano test1.txt', 'files'
    files_names = [f for f in listdir(my_path) if
                   isfile(join(my_path, f)) and not f.endswith(".xlsx") and not f.endswith(".csv")]
    if request.method == "POST":
        processed_text = request.form['choose_file']
        if processed_text in files_names:
            info, file = processed_text, processed_text
    f = open("files/" + file)
    r_message = f.readlines()
    return render_template('read_message.html', message=r_message, input_text=info, files_names=files_names)


to_server = []


@mqtt_client.on_connect()
def handle_connect(clent, userdata, flags, rc):
    if rc == 0:
        print('Połączono')
        mqtt_client.subscribe(topic)
    else:
        print(f'Nie udało się połączyć {rc}')
    to_server.clear()


@mqtt_client.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    to_server.append(data['payload'])
    if len(to_server) > 1:
        f = open("files/" + to_server[0], "a")
        f.write(data['payload'] + "\n")
    print(data['payload'])


@app.route('/get_mqtt', methods=['GET'])
def get_mqtt():
    return render_template('get_mqtt.html', lista=to_server)


if __name__ == '__main__':
    app.run(debug=True)
