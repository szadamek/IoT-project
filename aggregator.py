from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta
import ast


app = Flask(__name__)

# Słownik przechowujący dane otrzymane od generatorów
data = {}

def process_data(received_data, generator_ip):
    current_time = datetime.now()

    if generator_ip not in data:
        data[generator_ip] = {i: [] for i in range(len(received_data))}

    for i, value in enumerate(ast.literal_eval(received_data)):
        data[generator_ip][i].append((current_time, value))

    # Usun dane starsze niż 1 godzina
    for i in range(len(received_data)):
        data[generator_ip][i] = [x for x in data[generator_ip][i] if x[0] > current_time - timedelta(hours=1)]

def get_average(generator_ip):
    generator_data = data[generator_ip]

    averages = []
    for i in range(len(generator_data)):
        column_data = generator_data[i]
        if len(column_data) > 0:
            average = sum([x[1] for x in column_data]) / len(column_data)
            averages.append(average)
        else:
            averages.append(0)

    return averages




@app.route("/aggregate/<generator_id>", methods=["POST"])
def aggregate(generator_id):
    data = request.json
    print(f"{generator_id}: ", data)
    print(f"generator_id: {generator_id}")
    process_data(data, int(generator_id))

    return ""


@app.route("/configure", methods=["GET", "POST"])
def configure_aggregation():
    if request.method == "POST":
        # Pobierz konfigurację aplikacji agregującej z formularza
        aggregation_period = request.form["aggregation_period"]

        # Zapisz konfigurację do pliku lub bazy danych
        with open("aggregation_config.txt", "w") as f:
            f.write(aggregation_period)

    return render_template("configure_aggregation.html")


@app.route("/display")
def display_aggregate():
    data_average = {}

    if 1 in data:
        aggregate_value1 = get_average(1)
        data_average[1] = aggregate_value1
    else:
        data_average[1] = "Brak danych dla generatora o id {}".format(1)

    if 2 in data:
        aggregate_value2 = get_average(2)
        data_average[2] = aggregate_value2
    else:
        data_average[2] = "Brak danych dla generatora o id {}".format(2)

    if 3 in data:
        aggregate_value3 = get_average(3)
        data_average[3] = aggregate_value3
    else:
        data_average[3] = "Brak danych dla generatora o id {}".format(3)

    if 4 in data:
        aggregate_value4 = get_average(4)
        data_average[4] = aggregate_value4
    else:
        data_average[4] = "Brak danych dla generatora o id {}".format(4)

    if 5 in data:
        aggregate_value5 = get_average(5)
        data_average[5] = aggregate_value5
    else:
        data_average[5] = "Brak danych dla generatora o id {}".format(5)

    # Render the template and pass the values to the template as variables
    return render_template("agregator.html", data=data_average)



if __name__ == "__main__":
    app.run(debug=True, port=7000)
