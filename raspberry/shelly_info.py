import threading
from urllib.parse import urlencode
import requests
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime, timedelta
from time import sleep

class Shelly_info:
    def __init__(   self, 
                    db_update_interval = 10 * 60, 
                    shelly_fetch_interval = 10, 
                    service_account_file = 'clave_google.json',
                    project_id = 'paneles-solares-387716',
                    dataset_id = 'consumo_energia',
                    table_id = 'datos_consumo'
                ):
        self.db_update_interval = db_update_interval
        self.shelly_fetch_interval = shelly_fetch_interval
        self.shelly_url_placas = "http://raspfran.asuscomm.com:3544/emeter/0"
        self.shelly_url_red = "http://raspfran.asuscomm.com:3544/emeter/1"
        self.shelly_url_relay = "http://raspfran.asuscomm.com:3544/relay/0"
        self.service_account_file = service_account_file
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.periodic_upload = False
        self.periodic_upload_thread = None

    def __get_url(self, url):
        payload = {}
        headers = {
            'Authorization': 'Basic cDpv'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        return response.json()

    def get_placas_json(self):
        return self.__get_url(self.shelly_url_placas)

    def get_red_json(self):
        return self.__get_url(self.shelly_url_red)
    
    def get_data(self):
        datos_placas = self.get_placas_json()
        datos_red = self.get_red_json()

        return {
            "datetime": datetime.now(),
            "energia_generada_placas": datos_placas['power'],
            "energia_consumida_red": datos_red['power'],
            "voltaje": datos_red['voltage'],
        }
    
    def upload_to_BigQuery(self, json):
        # Autenticación con Google Cloud utilizando el archivo de credenciales de servicio
        credentials = service_account.Credentials.from_service_account_file(self.service_account_file)

        # Crear una instancia del cliente de BigQuery
        client = bigquery.Client(credentials=credentials, project=self.project_id)

        # Obtener la tabla en BigQuery
        table_ref = client.dataset(self.dataset_id).table(self.table_id)
        table = client.get_table(table_ref)

        error = client.insert_rows(table, [json])
        return error
    
    def get_data_and_update_to_BigQuery(self):
        json = self.get_data()

        return self.upload_to_BigQuery(json)
    
    def __periodic_upload_thread(self):
        last_upload_to_db = datetime.now()
        messures = {
            "energia_generada_placas": 0,
            "energia_consumida_red": 0,
            "voltaje": 0,
        }
        while self.periodic_upload:
            if datetime.now() - last_upload_to_db >= timedelta(seconds=self.db_update_interval):
                messures['datetime'] = datetime.now()
                # Pasar medidas a Wh
                messures['energia_generada_placas'] *= self.shelly_fetch_interval / 3600
                messures['energia_consumida_red'] *= self.shelly_fetch_interval / 3600

                messures['energia_generada_placas'] = round(messures['energia_generada_placas'], 2)
                messures['energia_consumida_red'] = round(messures['energia_consumida_red'], 2)
                messures['voltaje'] = round(messures['voltaje'], 2) 
                
                print("datos enviados: ", messures)
                self.upload_to_BigQuery(messures)

                messures = {
                    "energia_generada_placas": 0,
                    "energia_consumida_red": 0,
                    "voltaje": 0,
                }
                last_upload_to_db = datetime.now()
            
            datos_placas = self.get_placas_json()
            datos_red = self.get_red_json()

            messures = {
                "energia_generada_placas": messures['energia_generada_placas'] + datos_placas['power'],
                "energia_consumida_red": messures['energia_consumida_red'] + datos_red['power'],
                "voltaje": datos_red['voltage'],
            }

            sleep(self.shelly_fetch_interval)
        
    def start_periodic_upload(self):
        self.periodic_upload = True
        # Crear y iniciar el hilo
        self.periodic_upload_thread = threading.Thread(target=self.__periodic_upload_thread)
        self.periodic_upload_thread.start()

    def stop_periodic_upload(self):
        self.periodic_upload = False
        self.periodic_upload_thread.join()

    def set_configure(self, json):
        res = {}
        if 'db_update_interval' in json:
            res['db_update_interval'] = "Ok"
            self.db_update_interval = json['db_update_interval']
        if 'shelly_fetch_interval' in json:
            res['shelly_fetch_interval'] = "Ok"
            self.shelly_fetch_interval = json['shelly_fetch_interval']
        
        for k in json.keys():
            if k != 'shelly_fetch_interval' and k != 'db_update_interval':
                res[k] = "Unsoported parameter"
        
        return res
    
    def get_configure(self):
        json = {}
        json['db_update_interval'] = self.db_update_interval
        json['shelly_fetch_interval'] = self.shelly_fetch_interval
        return json
    
    def set_relay_status(self, turn="", timer=0):
        url = self.shelly_url_relay + "?"
        params = {}
        if turn != "":
            params['turn'] = turn
        if timer != 0:
            params['timer'] = timer
        print(url + urlencode(params))
        return self.__get_url(url + urlencode(params))

    def get_relay_status(self):
        return self.__get_url(self.shelly_url_relay)


