from flask import Flask, request, jsonify
from shelly_info import Shelly_info

app = Flask(__name__)
shelly = Shelly_info()

@app.route('/status', methods=['GET'])
def get_status():
    data = shelly.get_data()
    return jsonify(data)

@app.route('/configure', methods=['GET', 'POST'])
def configure():
    print(request.method)
    if request.method == 'POST':
        # Verificar si el cuerpo de la solicitud contiene un JSON válido
        if request.is_json:
            configuration = request.get_json()
            res = shelly.set_configure(configuration)
            return res, 200
        else:
            return 'Error: se esperaba un JSON en el cuerpo de la solicitud', 400
    
    elif request.method == 'GET':
        return shelly.get_configure(), 200

@app.route('/relay', methods=['GET'])
def relay():
    turn = ""
    timer = 0
    query_param = request.args.get('turn')
    if query_param is not None:
        turn = query_param

    query_param = request.args.get('timer')
    if query_param is not None:
        timer = query_param

    if turn == "" and timer == 0:
        return shelly.get_relay_status()
    
    if turn != "" or timer != 0:
        return shelly.set_relay_status(turn, timer)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
