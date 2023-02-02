
class Puerto:
    def __init__(self) -> None:
        #seccion de lectura
        self.ultimo_bit_recibido = -1 # es el utlimo bit correcto que se vio en el canal de recibo
        self.tiempo_recibiendo_bit = 0 # el tiempo que se lleva recibiendo el ultimo bit de recibo
        self.receptor_de_envios_por_ms = [] #guarda todo lo que se recibe en el ms, se vacia despues
        #seccion de transmision
        self.bit_envio = -1   # es el bit actual que se esta enviando
        self.tiempo_envio_bit = 0  # es el tiempo que se lleva enviando el bit actual
        #seccion de conexion
        self.cable_en_puerto = False # indica si hay un cable en el puerto
        self.esta_conectado = False # indica si esta conectado a otro dispositivo

    def conectado(self)->bool:
        """Retorna true si esta coenctado a otro dispositivo"""
        return self.esta_conectado

    def conectar(self)->None:
        """Indica que fue conectado a otro dispositivo"""
        self.cable_en_puerto = True
        self.esta_conectado = True
    
    def desconectar(self)->None:
        """Indica que fue desconectado de otro dispositivo"""
        self.esta_conectado = False

    def quitar_cable(self)->None:
        """Desconecta el cable del puerto"""
        self.desconectar()
        self.cable_en_puerto = False

    def reiniciar_receptor(self)->None:
        """Vacia el receptor de envios por ms"""
        self.receptor_de_envios_por_ms = []

    def recibir_bit(self,bit:int):
        self.receptor_de_envios_por_ms.append(bit)


