from re import S
from dispositivo import Dispositvo
from puertoHub import PuertoHub

class Hub(Dispositvo):
    def __init__(self, nombre: str, signal_time: int, cantidad_puertos:int) -> None:
        super().__init__(nombre, signal_time)
        self._cantidad_de_puertos = cantidad_puertos
        self.puertos = {p+1:PuertoHub(f'{nombre}_{p+1}',signal_time=signal_time) for p in range(cantidad_puertos)}


    def tipo_dispositivo(self) -> str:
        return 'hub'

    def transmitir(self,bit:int,tiempo:int,puerto:int)->None:
        self.puertos[puerto].transmitir(tiempo,bit)

    def recibir(self, bit: int, tiempo: int, puerto: int):
        self.puertos[puerto].recibir_bit(bit)

    def comprobar_estados(self, tiempo: int) -> None:  #----------------
        for puerto in self.puertos.values():
            puerto.comprobacion_transmision(tiempo, self._salida)
            puerto.comprobacion_lectura(tiempo,self._salida)

    def tiene_cable(self,puerto:int)->bool:
        """Indica si hay cable en el puerto"""
        return self.puertos[puerto].cable_en_puerto
    
    def esta_conectado(self,puerto:int)->bool:
        """Indica si esta conectado a otro dispositivo"""
        return self.puertos[puerto].conectado()

    def conectar_cable(self,puerto:int):
        """Se coloca un cable en el puerto"""
        self.puertos[puerto].cable_en_puerto = True

    def quitar_cable(self,puerto:int):
        """Se retira el cable del puerto"""
        self.puertos[puerto].quitar_cable()

    def conectar(self,puerto:int)->None:
        """Se conecta el puerto a otro puerto"""
        self.puertos[puerto].conectar()

    def desconectar(self,puerto:int)->None:
        """El dispositivo fue desconectado de otro puerto"""
        self.puertos[puerto].desconectar()

    def pendiente(self)->bool:
        """ Retorna True si quedan datos por enviar en el dispositivo"""
        return False