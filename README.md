#Descripción del Proyecto

Sistema desacoplado que lleva un control de los ingresos y egresos, tanto virtuales (que no involucran un movimiento bancario) como reales, entre distintas Cuentas.
***
#Servicios disponibles
##Listado de Batch
    GET http://127.0.0.1:8000/batches/
##Creación de Batch 
    POST http://127.0.0.1:8000/batches/

    {
        "description": "a description",
        "total_amount": 2,
            "date": "2019-01-04 10:00:00",
            "journals": [
                {
                    "gloss": "first movement",
                    "amount": "1.00000",
                    "date": "2012-12-12T12:12:00Z",
                    "incomeType": 1,
                    "from_account": 1,
                    "to_account": 2,
                    "assetType": 1
                },
                {
                    "gloss": "second movement",
                    "amount": "1.00000",
                    "date": "2012-12-12T12:12:00Z",
                    "incomeType": 1,
                    "from_account": 2,
                    "to_account": 1,
                    "assetType": 1
                }
            ]
        }

##Ejecución de Batch
    PUT http://127.0.0.1:8000/batches/137/
    
    {"state":2}
***
#Instalación del Proyecto

##Crear BD:
`CREATE SCHEMA 'cumplo_accountengine' DEFAULT CHARACTER SET utf8 ;`

##Instalar Virtualenv:

`pip3 install virtualenv`

`which virtualenv`

`which python3`

`virtualenv orm/ -p /usr/bin/python3`

Luego, activar el enviroment:

`source bin/activate`

##CONFIGURACIÓN INICIAL:
###En instalación manual
`pip install mysqlclient django djangorestframework`
###Generar requirements
`pip freeze > requirements.txt`
###Creación de Proyecto
`django-admin startproject accountengine`
###Creacion de App
`python manage.py startapp engine`

#USO GENERAL
###Actualización de requerimientos
`pip install -r requirements.txt`

###Migraciones:

Crea la migración
`python manage.py makemigrations`

Aplica las migraciones
`python manage.py migrate`

Genera Data inicial
`python manage.py dumpdata engine > initial_data.json`

Carga Data inicial
`python manage.py loaddata initial_data`