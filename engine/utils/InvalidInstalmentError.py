from service_objects.errors import InvalidInputsError

class InvalidInstalmentError(InvalidInputsError):

    """
    Excepción lanzada por errores en las entradas.

   Atributos:
       expresion -- expresión de entrada en la que ocurre el error
       mensaje -- explicación del error
   """


    def __init__(self, id, mensaje):
        self.id = id
        self.mensaje = mensaje