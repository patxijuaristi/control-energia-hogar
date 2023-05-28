import requests
from flask import Flask, render_template, request, redirect
from google.cloud import bigquery
from datetime import datetime

bigquery_client = bigquery.Client()

app = Flask(__name__)
app.config['STATIC_URL_PATH'] = '/static'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/estado')
def estado():
    url = 'http://raspfran.asuscomm.com:5000/status'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        # Extraer la información necesaria de la respuesta
        datetime_obj = datetime.strptime(data['datetime'], '%a, %d %b %Y %H:%M:%S %Z')
        formatted_datetime = datetime_obj.strftime('%d-%m-%Y %H:%M:%S')
        energia_consumida_red = data['energia_consumida_red']
        energia_generada_placas = data['energia_generada_placas']
        voltaje = data['voltaje']
        
        # Pass the extracted data to the template for rendering
        return render_template('estado.html', datetime=formatted_datetime, energia_consumida_red=energia_consumida_red, energia_generada_placas=energia_generada_placas, voltaje=voltaje)
    else:
        # Cuando el API falle, no mostrará datos
        return render_template('estado.html')

@app.route('/configuracion', methods=['GET', 'POST'])
def configuracion():
    url = 'http://raspfran.asuscomm.com:5000/configure'

    if request.method == 'GET':   
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            # Extraer la información necesaria de la respuesta
            db_update_interval = data['db_update_interval']
            shelly_fetch_interval = data['shelly_fetch_interval']
            
            # Pass the extracted data to the template for rendering
            return render_template('configuracion.html', db_update_interval=db_update_interval, shelly_fetch_interval=shelly_fetch_interval)
        else:
            # Cuando el API falle, no mostrará datos
            return render_template('configuracion.html', error_message='No se ha podido obtener la información sobre la configuración actual')
    else:
        # Obtener los valores ingresados por el usuario en el formulario
        db_update_interval = int(request.form['db_update_interval'])
        shelly_fetch_interval = int(request.form['shelly_fetch_interval'])

        # Construir el cuerpo de la solicitud
        data = {
            "db_update_interval": db_update_interval,
            "shelly_fetch_interval": shelly_fetch_interval
        }

        # Realizar la solicitud POST a la API
        response = requests.post(url, json=data)

        if response.status_code == 200:
            # Obtener la respuesta de la API en formato JSON
            api_response = response.json()

            if api_response['db_update_interval'] != 'Ok' or api_response['shelly_fetch_interval'] != 'Ok':
                error_message = "Error: No se pudo completar la solicitud"
                return render_template('configuracion.html', error_message=error_message)

            # Pasar los datos a la plantilla para renderizarlos
            return render_template('configuracion.html', api_response='Cambios realizados con éxito', db_update_interval=db_update_interval, shelly_fetch_interval=shelly_fetch_interval)
        else:
            # Mostrar un mensaje de error en caso de que la solicitud falle
            error_message = "Error: No se pudo completar la solicitud"
            return render_template('configuracion.html', error_message=error_message)

@app.route('/relay', methods=['GET', 'POST'])
def relay():
    url = 'http://raspfran.asuscomm.com:5000/relay'
    if request.method == 'GET':
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            # Extraer la información necesaria de la respuesta
            ison = data['ison']
            status = 'off'
            if ison:
                status = 'on'
            timer_duration = data['timer_duration']
            timer_remaining = data['timer_remaining']
            
            # Pass the extracted data to the template for rendering
            return render_template('relay.html', status=status, timer_duration=timer_duration, timer_remaining=timer_remaining)

    else:
        posturl = url
        status = request.form['status']
        minutes = int(request.form['minutes'])
        seconds = int(request.form['seconds'])
        total_seconds = (minutes * 60) + seconds

        if total_seconds != 0:
            if status == 'on':
                posturl = posturl + '?turn=on&timer=' + str(total_seconds)
            else:
                posturl = posturl + '?turn=off&timer=' + str(total_seconds)
        else:
            if status == 'on':
                posturl = posturl + '?turn=off'
            else:
                posturl = posturl + '?turn=on'
        
        print(posturl)

        response = requests.get(posturl)

        return redirect('/relay')

@app.route('/datos')
def datos():
    # Obtener parámetros de filtrado de la solicitud
    filter_datetime_start = request.args.get('filter_datetime_start')  # Fecha y hora de inicio para filtrar
    filter_datetime_end = request.args.get('filter_datetime_end')      # Fecha y hora de fin para filtrar
    order_by_field = request.args.get('order_by_field')                # Campo de ordenación
    order_by_direction = request.args.get('order_by_direction')        # Dirección de ordenación (ascendente o descendente)

    # Construir la consulta SQL con o sin filtrado por rango de fecha y hora
    squery = """
        SELECT *
        FROM `consumo_energia.datos_consumo`
    """

    if filter_datetime_start and filter_datetime_end:
        # Formatear las cadenas de fecha y hora en el formato correcto
        filter_datetime_start = datetime.strptime(filter_datetime_start, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
        filter_datetime_end = datetime.strptime(filter_datetime_end, '%Y-%m-%dT%H:%M').strftime('%Y-%m-%d %H:%M:%S')
        squery += f"""
            WHERE datetime >= DATETIME("{filter_datetime_start}")
              AND datetime <= DATETIME("{filter_datetime_end}")
        """

    if order_by_field and order_by_direction:
        squery += f"""
            ORDER BY {order_by_field} {order_by_direction}
        """
    else:
        # Ordenar por datetime de forma descendente por defecto si no se especifica ninguna ordenación
        squery += """
            ORDER BY datetime DESC
        """

    squery += """
        LIMIT 10
    """

    query = (squery)
    query_result = bigquery_client.query(query)

    results = [
        {
            'datetime': r['datetime'].replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S'),
            'energia_generada_placas': r['energia_generada_placas'],
            'energia_consumida_red': r['energia_consumida_red'],
            'voltaje': r['voltaje']
        }
        for r in query_result
    ]

    return render_template('ultimos_resultados.html', results=results)

if __name__ == '__main__':
    app.run(debug=True, port=8000)
