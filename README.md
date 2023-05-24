Control de energia del hogar ☀️🔋
===

Proyecto desarrollado para la asignatura de Industrialización y Despliegue de Sistemas IoT, que controla el consumo de energia de la red de un hogar y la cantidad de energia generada por las placas solares de dicho hogar. La energia se controla con un sensor Shelly, que mediante la Raspberry PI se conecta a una base de datos BigQuery en la nube de Google, y esos datos se muestran en una aplicación web de Flask desplegada en la nube de Google.

Para utilizar los scripts y el programa, primero es necesario crear un entorno virtual y luego instalar las dependencias necesarias con pip en él. Para ello se pueden utilizar los siguientes comandos:

```
virtualenv env
.\env\Scripts\activate

pip install -r .\requirements.txt
```

A continuación hay que configurar la variable de entorno de la URL de conexión a MongoDB. Para ello, copiaremos el fichero de ejemplo y lo editaremos incluyendo la URL de MongoDB. Se puede hacer con los siguientes comandos:

```
cp .env.sample .env
nano .env
```