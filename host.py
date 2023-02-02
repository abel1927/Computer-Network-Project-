from conversor import Conversor
from dispositivo import Dispositvo
from puerto import Puerto
from random import randint
from trama import Trama
import ip_packet
from detector import CRC
from detector import Hamming

class Host(Dispositvo):
    def __init__(self, nombre:str, signal_time:int, error_detection:str, max_colisiones:int=15,max_reintentos:int=200000) -> None:
        super().__init__(nombre, signal_time)
        self.error_detection = error_detection
        self.maximo_colisiones = max_colisiones
        self.maximo_reintentos = max_reintentos
        self.mac = ""
        self.ip = ''
        self.mascara = ''

        self._salida_data = open('output/'+nombre+'_data.txt','w')
        self._salida_packet=open('output/'+nombre+'_payload.txt','w')
        self.table_arp = {' ': ' '}
        self.ip_packets_pendientes = dict() #par ip_destino : lista de packets pendientes de enviar a esa ip
        self.ip_packets_censure = dict() #par ip_destino : lista de packets censurados                          #------------------aqui cambie---------------

        self.table_ruta = [] 
        
        self.puerto = Puerto()
        #seccion transmision
        self.data_envio = []  # son los bits a enviar
        self.transmitiendo = False # indica si se encuentra transmitiendo actualemente
        self.tiempo_empezar_envio = -1  # en que ms empezar a enviar, -1 si esta transmitiendo o no tiene nada
        self.colisiones_continuas = 0
        self.reintentos_continuos = 0
        #seccion lectura
        # trama
        self.trama = Trama()  # para conformar la trama
        self.lista_comenzar_tiempo_espera_ping = []
        self.contador_ms_ping = -1
        self.flag_parar_ping = False

    def obtener_mac(self,mac:str)->None:
        """Se le da su mac al host"""
        self.mac = mac

    def obtener_ip_mascara(self,ip:str, mascara:str)->None:
        """Se le da su ip y mascara al host"""
        self.ip = ip
        self.mascara = mascara

    def tipo_dispositivo(self) -> str:
        """host"""
        return "host"

    def estado_transmision(self,tiempo:int)->bool:
        """"Indica si la pc esta en disposicion de transmitir o transmitiendo en el ms actual"""
        if self.detectar_paso_ms_ping():
            return False
        return self.transmitiendo or self.tiempo_empezar_envio == tiempo

    def transmitir(self,tiempo:int)->int:
        """Realiza su transmision retorna el bit que transmitio"""
        bit = self.puerto.bit_envio
        self.transmitiendo = True
        return bit

    def recibir(self, bit: int, tiempo: int, puerto: int = 1):
        """Realiza la recepcion del bit por el canal de lectura"""
        self.puerto.recibir_bit(bit)

    def esta_conectado(self, puerto: int) -> bool:
        """Indica si esa conectado a otro dispositivo"""
        return self.puerto.conectado()

    def tiene_cable(self,puerto:int)->bool:
        """Indica si hay cable en el puerto"""
        return self.puerto.cable_en_puerto

    def conectar_cable(self, puerto: int):
        """Se conecta un cable en el puerto"""
        self.puerto.cable_en_puerto = True

    def quitar_cable(self, puerto: int):
        """Se retira el cable del puerto"""
        self.puerto.quitar_cable()

    def desconectar(self,puerto:int)->None:
        """El dispositivo fue desconectado de otro puerto"""
        self.puerto.desconectar()

    def conectar(self, puerto: int) -> None:
        """El dispositivo fue conectado a otro puerto"""
        self.puerto.conectar()

    def comprobar_estados(self, tiempo: int) -> None:
        self.__comprobar_transmision__(tiempo=tiempo)
        self.__comprobar_lectura__(tiempo=tiempo)

    def __reinciar_variables_envio__(self)->None:
        self.transmitiendo = False
        self.tiempo_empezar_envio = -1
        self.data_envio = []
        self.colisiones_continuas = 0
        self.reintentos_continuos = 0
        self.puerto.bit_envio = -1
        self.puerto.tiempo_envio_bit = 0

    def __comprobar_transmision__(self, tiempo: int) -> None:
        if self.flag_parar_ping:
            return
        if self.transmitiendo: # esta en transmision
            if not self.puerto.conectado():
                self.reintentos_continuos = self.reintentos_continuos + 1
                if self.reintentos_continuos == self.maximo_reintentos:
                    self.__reinciar_variables_envio__()
                    return
            hubo_colision = len(self.puerto.receptor_de_envios_por_ms)>1
            if hubo_colision:#hubo colision en la red
                self.reportar_envio(tiempo=tiempo,bit=self.puerto.bit_envio,estado="collision")
                self.colisiones_continuas = self.colisiones_continuas + 1
                if self.colisiones_continuas == self.maximo_colisiones:
                    self.__reinciar_variables_envio__()
                    # aqui ya para sus transmisiones, y es pierde la data
                else:
                    self.transmitiendo = False
                    self.tiempo_empezar_envio = tiempo + randint(0,10000)
                    self.puerto.tiempo_envio_bit = 0 # el bit que colisiono se enviara de nuevo desde el inicio
            else: # fue una transmision satisfactoria
                #aqui va un freno si esta en espera
                t_envio = self.puerto.tiempo_envio_bit
                if t_envio == 0:
                    self.colisiones_continuas = 0
                    self.reintentos_continuos = 0
                    self.reportar_envio(tiempo=tiempo,bit=self.puerto.bit_envio,estado="Ok")
                t_envio = t_envio + 1
                if t_envio == self.signal_time:
                    ###aqui va cuando termina un bit
                    self.detectar_bit_enviado_ping()
                    t_envio = 0
                    nuevo_bit = -1
                    if len(self.data_envio) > 0:#coge un nuevo bit para transmitir
                        nuevo_bit = self.data_envio.pop(0)
                    else:#se termino de enviar toda la data que tenia
                        self.__reinciar_variables_envio__()
                        return
                    self.puerto.bit_envio = nuevo_bit
                self.puerto.tiempo_envio_bit = t_envio

    def __comprobar_lectura__(self, tiempo: int) -> None:
        if len(self.puerto.receptor_de_envios_por_ms) == 0: # no recibo
            self.puerto.ultimo_bit_recibido = -1
            self.puerto.tiempo_recibiendo_bit = 0
            return
        bit_recibido = self.puerto.receptor_de_envios_por_ms.pop(0)
        for b in self.puerto.receptor_de_envios_por_ms:
            bit_recibido = bit_recibido^b
        if bit_recibido != self.puerto.ultimo_bit_recibido:
            self.reportar_lectura(tiempo=tiempo,bit=bit_recibido)
            self.trama.agregar_bit(bit=bit_recibido)
            if self.trama.completa:
                if self.trama.hexa_MAC_destino() == self.mac or self.trama.hexa_MAC_destino() == 'FFFF':
                    error = False
                    if self.detectar_solicitud_arp(trama=self.trama):
                        mac_destino = self.trama.hexa_MAC_origen()
                        self.enviar_arp_Response(tiempo=tiempo+1, mac_destino=mac_destino)
                    elif self.detectar_respuesta_arp(trama=self.trama):
                        datos = "".join(map(str,self.trama.datos))
                        ip_buscada = Conversor.binario_ip(datos[32:])
                        mac_buscada = self.trama.hexa_MAC_origen()
                        self.table_arp[ip_buscada] = mac_buscada
                        ips_encontradas = []
                        for ip in self.ip_packets_pendientes.keys():
                            if ip == ip_buscada:
                                for packet in self.ip_packets_pendientes[ip]:
                                    if ip_packet.is_ping_packet(packet):
                                        self.agregado_de_ping(tiempo=tiempo+1,mac_destino=mac_buscada,packet=packet)
                                        #self.agregar_trama_envio(tiempo=tiempo+1,mac_destino=mac_buscada,data=Conversor.binario_hexadecimal(packet.completo_binario()))
                                    else:  
                                        self.agregar_trama_envio(tiempo+1,mac_buscada, Conversor.binario_hexadecimal(packet.completo_binario()))
                                ips_encontradas.append(ip)       
                        for ip in ips_encontradas: del self.ip_packets_pendientes[ip]
                    else:
                        datos = self.trama.datos
                        if self.error_detection == 'crc':
                            error = not CRC.decodificar_trama_crc(datos + self.trama.bit_verificacion)
                        elif self.error_detection == 'hamming':
                            verificacion= self.trama.bit_verificacion
                            error = Hamming.decodificar_trama_hamming(datos,verificacion)
                        #lectura capa de red
                        self.verificar_packet(tiempo,datos)#------------------aqui cambie---------------
                    #lectura capa de enlace
                    self.reportar_lectura_trama(tiempo,self.trama.hexa_MAC_origen(), self.trama.hexa_datos(),error)   
                self.trama = Trama()
            self.puerto.ultimo_bit_recibido = bit_recibido
            self.puerto.tiempo_recibiendo_bit = 1
        else:
            if self.puerto.tiempo_recibiendo_bit + 1 == self.signal_time:
                    self.puerto.ultimo_bit_recibido = -1
                    self.puerto.tiempo_recibiendo_bit = 0
            else:
                self.puerto.tiempo_recibiendo_bit = self.puerto.tiempo_recibiendo_bit + 1
        self.puerto.reiniciar_receptor()

    def reportar_envio(self,tiempo:int,bit:int,estado:str)->None:
        self._salida.write(f'{tiempo} {self.nombre}_1 send {bit} {estado}\n')

    def reportar_lectura(self,tiempo:int,bit:int)->None:
        self._salida.write(f'{tiempo} {self.nombre}_1 read {bit}\n')

    def reportar_lectura_trama(self,tiempo:int,MAC_origen:str,datos:str,error:bool)->None:
        if error:
            self._salida_data.write(f'{tiempo} {MAC_origen} {datos} ERROR\n')
        else:
            self._salida_data.write(f'{tiempo} {MAC_origen} {datos}\n')

    def verificar_packet(self,tiempo:int,datos:str)->None:    #------------------aqui cambie---------------
        packet = ip_packet.crear_ip_packet2("".join(map(str,datos)))
        if Conversor.binario_decimal(packet.Protocolo) == 1:
            payload = Conversor.binario_decimal(packet.datos)
            if payload == 0:
                self.reportar_lectura_packet(tiempo,packet,"echo reply")
            if payload == 3:
                for ip in self.ip_packets_pendientes.keys():
                    if ip == packet.ip_destino:
                        self.ip_packets_censure[ip]=self.ip_packets_pendientes[ip]
                        del self.ip_packets_pendientes[ip]
                        break
                self.reportar_lectura_packet(tiempo,packet,"destination host unreachable")
            if payload == 8:
                self.pong(tiempo+1, packet.ip_origen)
                self.reportar_lectura_packet(tiempo,packet,"echo request")
            if payload == 11 :
                self.reportar_lectura_packet(tiempo,packet,"time exceeded")
        else:
            self.reportar_lectura_packet(tiempo,packet,"")


    def reportar_lectura_packet(self,tiempo:int,packet:ip_packet.IpPacket,protocolo:str)->None:
        if packet.ip_destino != self.ip:
            return
        ip_origen = packet.ip_origen
        datos = packet.datos
        if(Conversor.binario_decimal(packet.Protocolo)==1):
            self._salida_packet.write(f'{tiempo} {ip_origen} {datos} {protocolo}\n')
        else:
            self._salida_packet.write(f'{tiempo} {ip_origen} {datos}\n')


    def agragar_datos_envio(self,tiempo:int,datos:str)->None:
        """Agrega los nuevos bit al bus de envio"""
        for bit in datos:
            self.data_envio.append(int(bit))
        if self.puerto.bit_envio == -1:
            self.tiempo_empezar_envio = tiempo
            self.puerto.bit_envio = self.data_envio.pop(0)

    def __protocolo_codificar_data__(self, data:str)-> tuple:
        """ Retorna una tupla con el string de los bits del tamanho de verificacion
        y el string de los bits de la cadena de verificacion"""
        tamanho_verificacion,bits_verificacion = '',''
        if self.error_detection == 'crc':
            tamanho_verificacion,bits_verificacion = CRC.codificar_trama_crc([int(b) for b in Conversor.hexadecimal_binario(data)])
        elif self.error_detection == 'hamming':
            t,bits_verificacion = Hamming.codificar_trama_hamming([int(b) for b in Conversor.hexadecimal_binario(data)])
            tamanho_verificacion=Conversor.decimal_binario(int(t))
            pass
        return tamanho_verificacion,bits_verificacion

    def __crear_trama__(self, mac_destino:str, data:str)->str:
        """ Devuelve la trama como str """
        #mac_destino
        datos = Conversor.hexadecimal_binario(mac_destino)
        #mac_origen
        datos = datos + Conversor.hexadecimal_binario(self.mac)
        #tamnho_datos
        datos = datos + Conversor.decimal_binario(len(data)//2)
        ##-------
        tamanho_verificacion,bits_verificacion = self.__protocolo_codificar_data__(data)
        #tamanho_verificacion
        datos = datos + tamanho_verificacion
        #datos
        datos = datos + Conversor.hexadecimal_binario(data)
        #bit_recuperacion
        datos = datos + bits_verificacion
        ##
        return datos

    def agregar_trama_envio(self,tiempo:int, mac_destino:str, data:str)->None:
        """ Agrega la trama a los envios """
        #mac_destino
        datos = Conversor.hexadecimal_binario(mac_destino)
        #mac_origen
        datos = datos + Conversor.hexadecimal_binario(self.mac)
        #tamnho_datos
        datos = datos + Conversor.decimal_binario(len(data)//2)
        ##-------
        tamanho_verificacion,bits_verificacion = self.__protocolo_codificar_data__(data)
        #tamanho_verificacion
        datos = datos + tamanho_verificacion
        #datos
        datos = datos + Conversor.hexadecimal_binario(data)
        #bit_recuperacion
        datos = datos + bits_verificacion
        ##
        self.agragar_datos_envio(tiempo=tiempo,datos=datos)

    def agregar_ip_packet(self,tiempo:int, ip_destino:str, data:str)->None:#-------
        """ Agrega el paquete a la trama"""
        mac_destino = ''
        #creo el packet completo
        packet = ip_packet.crear_ip_packet(ip_destino=ip_destino, ip_origen=self.ip, data = data)
        if not ip_destino in self.table_arp.keys() or self.table_arp[ip_destino] == '': #si no tengo la mac
            #self.ip_packets.append(packet)  # lista de los que quedan pendientes
            if self.ip_packets_pendientes.get(ip_destino) == None:
                self.ip_packets_pendientes[ip_destino] = []
            self.ip_packets_pendientes[ip_destino].append(packet)
            self.table_arp[ip_destino] = ''
            self.enviar_arp_Query(tiempo=tiempo, ip_destino=ip_destino)
            return
        mac_destino = self.table_arp[ip_destino]
        # envio el pakete completo
        self.agregar_trama_envio(tiempo=tiempo,mac_destino=mac_destino,data=Conversor.binario_hexadecimal(packet.completo_binario()))


    def agregado_de_ping(self, tiempo:int, mac_destino:str, packet:ip_packet.IpPacket)->None:
        trama_ping = self.__crear_trama__(mac_destino=mac_destino, data=Conversor.binario_hexadecimal(packet.completo_binario()))
        Z = len(trama_ping)
        X = len(self.data_envio)
        self.lista_comenzar_tiempo_espera_ping.append(X+Z)
        self.lista_comenzar_tiempo_espera_ping.append(X+2*Z)
        self.lista_comenzar_tiempo_espera_ping.append(X+3*Z)
        self.agragar_datos_envio(tiempo=tiempo, datos=trama_ping*4)

    def detectar_paso_ms_ping(self)->bool:
        if self.flag_parar_ping:
            self.contador_ms_ping -= 1
            if self.contador_ms_ping == 0:
                self.flag_parar_ping = False
        return self.flag_parar_ping

    def detectar_bit_enviado_ping(self):
        if len(self.lista_comenzar_tiempo_espera_ping) == 0:
            return
        for i in range(len(self.lista_comenzar_tiempo_espera_ping)):
            self.lista_comenzar_tiempo_espera_ping[i] -= 1
        if self.lista_comenzar_tiempo_espera_ping[0] == 0:
            self.lista_comenzar_tiempo_espera_ping.pop(0)
            self.flag_parar_ping = True
            self.contador_ms_ping = 100


    def ping(self, tiempo:int, ip_destino: str) -> None:  #------------------aqui cambie---------------
        packet=ip_packet.crear_ip_packet_ping(ip_destino, self.ip)
        if not ip_destino in self.table_arp.keys() or self.table_arp[ip_destino] == '': #si no tengo la mac
            #self.ip_packets.append(packet)  # lista de los que quedan pendientes
            if self.ip_packets_pendientes.get(ip_destino) == None:
                self.ip_packets_pendientes[ip_destino] = []
            self.ip_packets_pendientes[ip_destino].append(packet)
            self.table_arp[ip_destino] = ''
            self.enviar_arp_Query(tiempo=tiempo, ip_destino=ip_destino)
            return
        mac_destino = self.table_arp[ip_destino]
        # envio el pakete completo
        self.agregado_de_ping(tiempo=tiempo, mac_destino=mac_destino, packet=packet)
        #for i in range(4):
        #    self.agregar_trama_envio(tiempo=tiempo,mac_destino=mac_destino,data=Conversor.binario_hexadecimal(packet.completo_binario()))



    def pong(self, tiempo:int, ip_destino: str) -> None: #------------------aqui cambie---------------
        packet=ip_packet.crear_ip_packet_pong(ip_destino, self.ip)
        if not ip_destino in self.table_arp.keys() or self.table_arp[ip_destino] == '': #si no tengo la mac
            #self.ip_packets.append(packet)  # lista de los que quedan pendientes
            if self.ip_packets_pendientes.get(ip_destino) == None:
                self.ip_packets_pendientes[ip_destino] = []
            self.ip_packets_pendientes[ip_destino].append(packet)
            self.table_arp[ip_destino] = ''
            self.enviar_arp_Query(tiempo=tiempo, ip_destino=ip_destino)
            return
        mac_destino = self.table_arp[ip_destino]
        # envio el pakete completo
        self.agregar_trama_envio(tiempo=tiempo,mac_destino=mac_destino,data=Conversor.binario_hexadecimal(packet.completo_binario()))


    def detectar_solicitud_arp(self,trama:Trama):
        if 1 in trama.tamanho_verificacion:
            return False
        ARPQ = '01000001010100100101000001010001'
        if ARPQ == "".join(map(str,trama.datos[0:32])):
            return self.ip == Conversor.binario_ip("".join(map(str,trama.datos[32:])))
        return False


    def enviar_arp_Query(self,tiempo:int, ip_destino:str):
        ARPQ = '01000001010100100101000001010001'
        #mac_destino
        datos = Conversor.hexadecimal_binario('FFFF')
        #mac_origen
        datos = datos + Conversor.hexadecimal_binario(self.mac)
        #tamnho_datos
        datos = datos + Conversor.decimal_binario(8)
        #tamanho_verificacion
        datos = datos + '00000000'
        #datos
        datos = datos + ARPQ
        datos = datos + Conversor.ip_binario(ip_destino)
        self.agragar_datos_envio(tiempo=tiempo,datos=datos)


    def detectar_respuesta_arp(self,trama:Trama):
        if 1 in trama.tamanho_verificacion:
            return False
        ARPR = '01000001010100100101000001010010'
        if ARPR == "".join(map(str,trama.datos[0:32])):
            return self.mac == trama.hexa_MAC_destino()
        return False


    def enviar_arp_Response(self, tiempo:int, mac_destino:str):
        ARPR = '01000001010100100101000001010010'
        #mac_destino
        datos = Conversor.hexadecimal_binario(mac_destino)
        #mac_origen
        datos = datos + Conversor.hexadecimal_binario(self.mac)
        #tamnho_datos
        datos = datos + Conversor.decimal_binario(8)
        #tamanho_verificacion
        datos = datos + '00000000'
        #datos
        datos = datos + ARPR
        datos = datos + Conversor.ip_binario(self.ip)
        self.agragar_datos_envio(tiempo=tiempo,datos=datos)


    def fin_transmision(self):
        super().fin_transmision()
        self._salida_data.close()


    def pendiente(self) -> bool:
        return len(self.data_envio) > 0 or self.puerto.bit_envio != -1

