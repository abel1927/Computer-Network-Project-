from puerto import Puerto

class PuertoHub(Puerto):
    def __init__(self,id_puerto:str,signal_time:int) -> None:
        super().__init__()
        self.id_puerto = id_puerto
        self.signal_time = signal_time
        self.bit_enviados_en_ms = []

    def transmitir(self,tiempo,bit):
        self.bit_enviados_en_ms.append(bit)

    def comprobacion_transmision(self,tiempo:int,salida):
        if self.conectado() and len(self.bit_enviados_en_ms)>0:
            bit_enviado = self.bit_enviados_en_ms.pop(0)
            for b in self.bit_enviados_en_ms:
                bit_enviado = bit_enviado^b
            if bit_enviado == self.bit_envio:
                self.tiempo_envio_bit = self.tiempo_envio_bit + 1
                if self.tiempo_envio_bit == self.signal_time:
                    self.tiempo_envio_bit = 0
                    self.bit_envio = -1
                    self.bit_enviados_en_ms = []
                    return
            else:
                self.reportar_envio(tiempo=tiempo,bit=bit_enviado,file=salida)
                self.bit_envio = bit_enviado
                self.tiempo_envio_bit = 1
        else:
            bit_enviado = -1
        self.bit_enviados_en_ms = []

    def comprobacion_lectura(self, tiempo:int,salida):
        if len(self.receptor_de_envios_por_ms) == 0: # no recibo
            self.ultimo_bit_recibido = -1
            self.tiempo_recibiendo_bit = 0
            return
        bit_recibido = self.receptor_de_envios_por_ms.pop(0)
        for b in self.receptor_de_envios_por_ms:
            bit_recibido = bit_recibido^b
        if bit_recibido != self.ultimo_bit_recibido:
            self.reportar_lectura(tiempo, bit_recibido, salida)
            self.ultimo_bit_recibido = bit_recibido
            self.tiempo_recibiendo_bit = 1
        else:
            if self.tiempo_recibiendo_bit + 1 == self.signal_time:
                self.ultimo_bit_recibido = -1
                self.tiempo_recibiendo_bit = 0
            else:
                self.tiempo_recibiendo_bit = self.tiempo_recibiendo_bit + 1
        self.reiniciar_receptor()

    def reportar_envio(self,tiempo:int,bit:int, file)->None:
        file.write(f'{tiempo} {self.id_puerto} send {bit}\n')

    def reportar_lectura(self,tiempo:int,bit:int, file)->None:
        file.write(f'{tiempo} {self.id_puerto} receive {bit}\n')