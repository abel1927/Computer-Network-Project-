from os import times
from dispositivo import Dispositvo
from puertoSw import PuertoSw

class Switch(Dispositvo):
    def __init__(self, nombre:str, signal_time:int,cantidad_puertos:int) -> None:
        super().__init__(nombre, signal_time)
        self._cantidad_de_puertos = cantidad_puertos
        self.tabla_mac = {} # mac: [puerto,tiempo_ultima_vez]
        self.puertos = {p+1:PuertoSw(f'{nombre}_{p+1}',signal_time=signal_time) for p in range(cantidad_puertos)}

    def tipo_dispositivo(self) -> str:
        return "switch"

    def estado_transmision(self,tiempo:int,puerto:int)->bool:
        """"Indica si el puerto esta en disposicion de transmitir o transmitiendo en el ms actual"""
        return self.puertos[puerto].transmision()

    def transmitir(self,tiempo:int,puerto:int)->int:
        """Realiza su transmision retorna el bit que transmitio"""
        return self.puertos[puerto].bit_envio

    def recibir(self, bit: int, tiempo: int, puerto: int):
        """Realiza la recepcion del bit por el canal de lectura del puerto"""
        self.puertos[puerto].recibir_bit(bit)

    def comprobar_estados(self, tiempo: int) -> None:
        for p,puerto in self.puertos.items():
            puerto.comprobar_transmision(tiempo, self._salida)
            trama = puerto.comprobar_lectura(tiempo, self._salida)
            if trama != None:
                mac_origen = trama.hexa_MAC_origen()
                self.tabla_mac[mac_origen] = [p, tiempo]
                mac_destino = trama.hexa_MAC_destino()
                datos = trama.completa_binario()
                if mac_destino == "FFFF" or self.tabla_mac.get(mac_destino) == None:
                    for id_puerto in self.puertos.keys():
                        if id_puerto != p:
                            self.puertos[id_puerto].recibir_datos(datos)
                else:
                    puerto_tiempo = self.tabla_mac.get(mac_destino)
                    if tiempo - puerto_tiempo[1] < 180000:# si lo vi hace menos de 3 minutos
                        if puerto_tiempo[0] != p:
                            self.puertos[puerto_tiempo[0]].recibir_datos(datos)
                    else:
                        del self.tabla_mac[mac_destino]
                        for id_puerto in self.puertos.keys():
                            if id_puerto != p:
                                self.puertos[id_puerto].recibir_datos(datos)
        for puerto in self.puertos.values():
            puerto.cargar_backup()


    def tiene_cable(self, puerto: int) -> bool:
        """Indica si hay cable en el puerto"""
        return self.puertos[puerto].cable_en_puerto

    def esta_conectado(self, puerto: int) -> bool:
        """Indica si esta conectado a otro dispositivo"""
        return self.puertos[puerto].conectado()

    def conectar_cable(self, puerto: int):
        """Se coloca un cable en el puerto"""
        self.puertos[puerto].cable_en_puerto = True

    def quitar_cable(self, puerto: int):
        """Se retira el cable del puerto"""
        self.puertos[puerto].quitar_cable()

    def conectar(self, puerto: int) -> None:
        """Se conecta el puerto a otro puerto"""
        self.puertos[puerto].conectar()

    def desconectar(self, puerto: int) -> None:
        """El dispositivo fue desconectado de otro puerto"""
        self.puertos[puerto].desconectar()

    def pendiente(self) -> bool:
        """ Retorna True si quedan datos por enviar en el dispositivo"""
        for puerto in self.puertos.values():
            if puerto.transmision():
                return True
        return False
