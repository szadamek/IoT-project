import pandas as pd
import functions as f
import json
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


@app.route('/change', methods=['POST'])
def get_config():
    data = request.json
    with open("config3.json", "w") as file_t:
        file_t.write(json.dumps(data))
    global change_
    change_ = True
    return ""


def send_():
    file = open("config3.json")
    read = json.load(file)
    file.close()
    for i in list_t:
        global change_
        if change_:
            file = open("config3.json")
            read = json.load(file)
            file.close()
        if read['change'] == "start":
            f.send(i, read['type_of_send'], read['address'], int(read['frequency']), read['ip'], read['file_name'])
        else:
            print("Wysyłanie zatrzymane.")
            while True:
                if change_:
                    file = open("config3.json")
                    read = json.load(file)
                    file.close()
                    if read['change'] == "start":
                        break
                time.sleep(1)


if __name__ == "__main__":
    t1 = threading.Thread(target=send_)
    t1.start()
    app.run(debug=False, port=8002)
