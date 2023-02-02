from puertoSw import PuertoSw


class PuertoRt(PuertoSw):
    def __init__(self, id_puerto, signal_time: int, max_reintentos: int=200000) -> None:
        super().__init__(id_puerto, signal_time, max_reintentos=max_reintentos)
        self.mac = ''
        self.ip = ''
        self.mascara = ''

    def obtener_mac(self, mac:str)->None:
        self.mac = mac

    def obtener_ip_mascara(self, ip:str, mascara:str)->None:
        self.ip = ip
        self.mascara = mascara