from conversor import Conversor
from dispositivo import Dispositvo
from puerto import Puerto
from random import randint
from trama import Trama
import ip_packet
from detector import CRC
from detector import Hamming

class Ruta:
    def __init__(self, destination: str, mask: str, gateway:str,interfaz:int) -> None:
        self.destination = destination
        self.mask = mask
        self.gateway = gateway
        self.interfaz = interfaz # el puerto 

    
    def compare(self, ruta)-> bool:
        if(self.destination != ruta.destination):
            return False
        if(self.mask != ruta.mask):
            return False
        if(self.gateway != ruta.gateway):
            return False
        if(self.interfaz != ruta.interfaz):
            return False
        return True
        




        
        