import sys

from flask import Flask, render_template, request
from google.cloud import bigquery
from datetime import datetime

bigquery_client = bigquery.Client()

app = Flask(__name__)
app.config['STATIC_URL_PATH'] = '/static'

@app.route('/')
def home():
    return render_template('home.html')

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
