from puerto import Puerto
from trama import Trama

class PuertoSw(Puerto):
    def __init__(self,id_puerto,signal_time:int,max_reintentos:int=200000) -> None:
        super().__init__()
        self.id_puerto = id_puerto
        self.trama_recibo = Trama()
        self.data_envio = []
        self._backup_de_datos = [] # nuevos datos a emepzar a enviar en tiempo+1
        self.signal_time = signal_time
        self.maximo_reintentos = max_reintentos
        self.reintentos_continuos = 0

    def transmision(self)->bool:
        return self.bit_envio != -1

    def comprobar_transmision(self, tiempo:int, salida):
        if self.transmision():
            if not self.conectado():
                self.reintentos_continuos = self.reintentos_continuos +1
                if self.reintentos_continuos == self.maximo_reintentos:
                    self.data_envio = []
                    self.bit_envio = -1
                    self.tiempo_envio_bit = 0
                    self.reintentos_continuos = 0
            else:
                t_envio = self.tiempo_envio_bit
                if t_envio == 0:
                    self.reintentos_continuos = 0
                    self.reportar_envio(tiempo, self.bit_envio, salida)
                t_envio = t_envio + 1
                if t_envio == self.signal_time:
                    t_envio = 0
                    nuevo_bit = -1
                    if len(self.data_envio) > 0:#coge un nuevo bit para transmitir
                        nuevo_bit = self.data_envio.pop(0)
                    else:
                        self.data_envio = []
                        self.bit_envio = -1
                        self.tiempo_envio_bit = 0
                        self.reintentos_continuos = 0
                        return
                    self.bit_envio = nuevo_bit
                self.tiempo_envio_bit = t_envio

    def comprobar_lectura(self, tiempo: int, salida) -> Trama:
        if len(self.receptor_de_envios_por_ms) == 0: # no recibo
            self.ultimo_bit_recibido = -1
            self.tiempo_recibiendo_bit = 0
            return None
        trama_retorno = None
        bit_recibido = self.receptor_de_envios_por_ms.pop(0)
        for b in self.receptor_de_envios_por_ms:
            bit_recibido = bit_recibido^b
        if bit_recibido != self.ultimo_bit_recibido:
            self.reportar_lectura(tiempo, bit_recibido, salida)
            if self.trama_recibo.agregar_bit(bit=bit_recibido):
                trama_retorno = self.trama_recibo
                self.trama_recibo = Trama()
            self.ultimo_bit_recibido = bit_recibido
            self.tiempo_recibiendo_bit = 1
        else:
            if self.tiempo_recibiendo_bit + 1 == self.signal_time:
                    self.ultimo_bit_recibido = -1
                    self.tiempo_recibiendo_bit = 0
            else:
                self.tiempo_recibiendo_bit = self.tiempo_recibiendo_bit + 1
        self.reiniciar_receptor()
        return trama_retorno

    def reportar_lectura(self,tiempo:int,bit:int, file)->None:
        file.write(f'{tiempo} {self.id_puerto} receive {bit}\n')

    def reportar_envio(self,tiempo:int,bit:int, file)->None:
        file.write(f'{tiempo} {self.id_puerto} send {bit}\n')

    def recibir_datos(self, datos:list)->None:
        for b in datos:
            self._backup_de_datos.append(b)

    def cargar_backup(self)->None:
        while len(self._backup_de_datos) > 0:
            self.data_envio.append(self._backup_de_datos.pop(0))
        if self.bit_envio == -1 and len(self.data_envio) > 0:
            self.bit_envio = self.data_envio.pop(0)
            self.tiempo_envio_bit = 0

