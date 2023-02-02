
class Dispositvo:
    def __init__(self,nombre:str,signal_time:int) -> None:
        self.nombre = nombre
        self.signal_time = signal_time
        self._salida = open('output/'+nombre+'.txt','w')

    def recibir(self,bit:int,tiempo:int,puerto:int):
        pass

    def tiene_cable(self,puerto:int)->bool:
        """Indica si hay cable en el puerto"""
        pass

    def esta_conectado(self,puerto:int)->bool:
        """Indica si esta conectado a otro dispositivo"""
        pass

    def conectar_cable(self,puerto:int):
        """Se coloca un cable en el puerto"""
        pass

    def quitar_cable(self,puerto:int):
        """Se retira el cable del puerto"""
        pass

    def conectar(self,puerto:int)->None:
        """Se conecta el puerto a otro puerto"""
        pass

    def desconectar(self,puerto:int)->None:
        """El dispositivo fue desconectado de otro puerto"""
        pass

    def tipo_dispositivo(self)->str:
        """Indica el tipo de dispositivo"""
        pass

    def comprobar_estados(self,tiempo:int)->None:
        """En este metodo los dispositivo deben comprobar todo lo ocurrido 
        en un ms de transmision en la red"""
        pass

    def fin_transmision(self):
        """Cierra el log del dispositivo"""
        self._salida.close()

    def pendiente(self)->bool:
        """ Retorna True si quedan datos por enviar en el dispositivo"""
        pass