from conversor import Conversor

class Trama:
    def __init__(self) -> None:
        self.MAC_destino = []
        self.MAC_origen = []
        self.tamanho_datos = []
        self.tamanho_verificacion = []
        self.datos = []
        self.bit_verificacion = []
        self.len_datos = -1
        self.len_verificacion = -1
        self.completa = False

    def agregar_bit(self,bit:int)->bool:
        """ Devuelve True si la trama esta completa"""
        if len(self.MAC_destino) < 16:
            self.MAC_destino.append(bit)
        elif len(self.MAC_origen) < 16:
            self.MAC_origen.append(bit)
        elif len(self.tamanho_datos) < 8:
            self.tamanho_datos.append(bit)
            if len(self.tamanho_datos) == 8:
                binario = "".join(map(str,self.tamanho_datos))
                self.len_datos = int(binario,2)*8          
        elif len(self.tamanho_verificacion) < 8:
            self.tamanho_verificacion.append(bit)
            if len(self.tamanho_verificacion) == 8:
                binario = "".join(map(str,self.tamanho_verificacion))
                self.len_verificacion = int(binario,2)*8
        elif len(self.datos) < self.len_datos:
            self.datos.append(bit)
            if self.len_datos == len(self.datos) and self.len_verificacion == 0:
                self.completa=True
                return True
        elif len(self.bit_verificacion) < self.len_verificacion:
            self.bit_verificacion.append(bit)
            if len(self.bit_verificacion) == self.len_verificacion:
                self.completa=True
                return True
        return False

    def hexa_MAC_destino(self)->str:
        return Conversor.binario_hexadecimal("".join(map(str,self.MAC_destino)))

    def hexa_MAC_origen(self)->str:
        return Conversor.binario_hexadecimal("".join(map(str,self.MAC_origen)))

    def hexa_datos(self)->str:
        return Conversor.binario_hexadecimal("".join(map(str,self.datos)))

    def completa_binario(self)->list:
        binario = []
        for b in self.MAC_destino:
            binario.append(b)
        for b in self.MAC_origen:
            binario.append(b)
        for b in self.tamanho_datos:
            binario.append(b)
        for b in self.tamanho_verificacion:
            binario.append(b)
        for b in self.datos:
            binario.append(b)
        for b in self.bit_verificacion:
            binario.append(b)
        return binario
