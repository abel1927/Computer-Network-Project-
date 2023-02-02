from puertoRt import PuertoRt
from conversor import Conversor
from dispositivo import Dispositvo
from ruta import Ruta

class Router(Dispositvo):
    def __init__(self, nombre: str, signal_time: int, cantidad_puertos:int) -> None:
        super().__init__(nombre, signal_time)
        self._cantidad_de_puertos = cantidad_puertos
        self.puertos = {p+1:PuertoRt(f'{nombre}_{p+1}',signal_time=signal_time) for p in range(cantidad_puertos)}

        self.table_ruta = [] 

        

    ## le agregue la interface, ahora de aqui en este metodo hay que llamar a un metod 
    #en el puerto donde se le diga , puerto#interfaz coge tu mac
    def obtener_mac(self,mac:str, interface:int)->None:
        """Se le da su mac al puerto del router"""
        self.puertos[interface].obtener_mac(mac=mac)

    ## le agregue la interface, ahora de aqui en este metodo hay que llamar a un metod 
    #en el puerto donde se le diga , puerto#interfaz coge tu ip y mas...
    def obtener_ip_mascara(self,ip:str, mascara:str, interface:int)->None:
        """Se le da su ip y mascara al puerto del router"""
        self.puertos[interface].obtener_ip_mascara(ip=ip, mascara=mascara)

    def tipo_dispositivo(self) -> str:
        """router"""
        return "router"

    def reset(self) -> None:
        self.table_ruta.clear()

    def add(self,destination, mask, gateway,cantidad_puertos) -> None: #lo cambie para que siempre este en orden de prioridad a la hora de enrolar el pakt
        ruta= Ruta(destination, mask, gateway,cantidad_puertos)
        cont=self.contains(ruta)
        if not  cont[0]:
            priori=self.priority(Conversor.ip_binario(mask))
            if(len(self.table_ruta)==0):
                self.table_ruta.append((ruta,priori))
            else:
                pos=None
                for i in range(0,len(self.table_ruta)):
                    if(priori >= self.table_ruta[i][1]):
                        pos=i
                        break
                añadir=(ruta,priori)
                if(pos!=None):
                    self.table_ruta.insert(i,añadir)
                else:
                    self.table_ruta.append(añadir)
    
    def delete(self,destination, mask, gateway,cantidad_puertos) -> None:
        rutaDelete=Ruta(destination, mask, gateway,cantidad_puertos)
        b, ruta=self.contains(rutaDelete)
        if b:
            self.table_ruta.pop(ruta)
        
    def priority(self, mask) -> int:
        ones=0
        for i in range(0, len(mask)):
            if mask[i]=='1':
                ones+=1
        return ones
        
    def contains(self,ruta) ->tuple:
        for i in range(len(self.table_ruta)):
            if(self.table_ruta[i][0].compare(ruta)):
                return (True,i)
        return (False, None)


################----------------------------------------------------------->

    def estado_transmision(self,tiempo:int,puerto:int)->bool:
        """"Indica si el puerto esta en disposicion de transmitir o transmitiendo en el ms actual"""
        return self.puertos[puerto].transmision()

    def transmitir(self,tiempo:int,puerto:int)->int:
        """Realiza su transmision retorna el bit que transmitio"""
        return self.puertos[puerto].bit_envio

    def recibir(self, bit: int, tiempo: int, puerto: int):
        """Realiza la recepcion del bit por el canal de lectura del puerto"""
        self.puertos[puerto].recibir_bit(bit)

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

    def comprobar_estados(self, tiempo: int) -> None:
        # el analisis se hace por cada puerto xq se puede recibir a la vez x distintos lugares
        for p,puerto in self.puertos.items():
            puerto.comprobar_transmision(tiempo, self._salida)
            trama = puerto.comprobar_lectura(tiempo, self._salida)
            if trama != None:
                datos = ''.join(map(str,trama.datos))
                ip_datos = datos[0:32]
                broadcast=ip_datos[24:32]
                if self.priority(broadcast) == 8:
                    break
                mark=False
                for i in range(0, len(self.table_ruta)):
                    ruta = self.table_ruta[i][0]
                    ruta_mask = Conversor.ip_binario(ruta.mask)
                    _and = Conversor.decimal_binario( int(ip_datos,2) & int(ruta_mask,2)) #aquiiii ver el and
                    ruta_destination=Conversor.ip_binario(ruta.destination)
                    if(_and == ruta_destination):
                        mark=True
                        for id_puerto in self.puertos.keys():
                            if id_puerto == ruta.interfaz:
                                self.puertos[id_puerto].recibir_datos(datos)
                                break
                
                if(not mark):
                    a=1
                    #enviarle al host de origen un paquete ICMP

        for puerto in self.puertos.values():
            puerto.cargar_backup()