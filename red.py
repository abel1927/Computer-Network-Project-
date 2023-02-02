 from dispositivo import Dispositvo
from host import Host
from hub import Hub
from switch import Switch
from router import Router
from ruta import Ruta
from re import S, findall

class Red:
    def __init__(self,configuraciones:dict) -> None:
        self.dict_configuraciones = configuraciones
        self.signal_time = self.dict_configuraciones['signal_time']
        self.grafo_red = {}
        self.host_en_red = {}
        self.hubs_en_red = {}
        self.switch_en_red = {}
        self.router_en_red = {}

    def __contiene__(self,disp:str)->bool:
        return disp in self.grafo_red.keys()

    def create_host(self,nombre_dispositivo:str):
        """Agrega un nuevo host a la red"""
        if not self.__contiene__(nombre_dispositivo):
            error_det = self.dict_configuraciones['error_detection']
            pc = Host(nombre=nombre_dispositivo,signal_time=self.signal_time,error_detection=error_det)
            self.host_en_red[nombre_dispositivo]=pc
            self.grafo_red[nombre_dispositivo] = [None]
        else:
            print(f'Ya existe un dispositivo con nombre {nombre_dispositivo} en la red. '+
            'Instrucción invalidada!!!')

# agregue esto--> ENCAPSULA LO de la mac para los dos tipos %
    def mac_dispositivo(self, nombre_dispositivo:str, mac:str, interface:int)->None:
        if not self.__contiene__(nombre_dispositivo):
            print(f'No existe un dispositivo con nombre {nombre_dispositivo} en la red. '+
            'Instrucción invalidada!!!')
            return
        if self.host_en_red.get(nombre_dispositivo) != None:
            self.host_en_red[nombre_dispositivo].obtener_mac(mac)
        else:
            self.router_en_red[nombre_dispositivo].obtener_mac(mac,interface)

# agregue esto--> ENCAPSULA LO de la mac para los dos tipos %
    def ip_dispositvo(self, nombre_dispositivo:str, ip:str, mascara:str, interface:int)->None:
        if not self.__contiene__(nombre_dispositivo):
            print(f'No existe un dispositivo con nombre {nombre_dispositivo} en la red. '+
            'Instrucción invalidada!!!')
            return
        if self.host_en_red.get(nombre_dispositivo) != None:
            self.host_en_red[nombre_dispositivo].obtener_ip_mascara(ip, mascara)
        else:
            self.router_en_red[nombre_dispositivo].obtener_ip_mascara(ip, mascara, interface)


    def create_hub(self, nombre_dispositivo: str, numero_puertos: int) -> None:
        """Agrega un nuevo hub a la red"""
        if not self.__contiene__(nombre_dispositivo):
            hub = Hub(nombre_dispositivo,self.signal_time,numero_puertos)
            self.hubs_en_red[nombre_dispositivo]=hub
            self.grafo_red[nombre_dispositivo] = [None]*numero_puertos
        else:
            print(f'Ya existe un dispositivo con nombre {nombre_dispositivo} en la red. '+
            'Instrucción invalidada!!!')

    def create_switch(self, nombre_dispositivo: str, numero_puertos: int) -> None:
        """Agrega un nuevo switch a la red"""
        if not self.__contiene__(nombre_dispositivo):
            sw = Switch(nombre_dispositivo,self.signal_time,numero_puertos)
            self.switch_en_red[nombre_dispositivo] = sw
            self.grafo_red[nombre_dispositivo] = [None]*numero_puertos
        else:
            print(f'Ya existe un dispositivo con nombre {nombre_dispositivo} en la red. '+
            'Instrucción invalidada!!!')

    def create_router(self, nombre_dispositivo: str, numero_puertos: int) -> None:#---------------claudia---------------
        """Agrega un nuevo router a la red"""
        if not self.__contiene__(nombre_dispositivo):
            rt = Router(nombre_dispositivo,self.signal_time,numero_puertos)
            self.router_en_red[nombre_dispositivo] = rt
            self.grafo_red[nombre_dispositivo] = [None]*numero_puertos
        else:
            print(f'Ya existe un dispositivo con nombre {nombre_dispositivo} en la red. '+
            'Instrucción invalidada!!!')


    def route_reset(self,nombre_dispositivo:str):#---------------claudia---------------
        if self.__contiene__(nombre_dispositivo):
            rt:Router = self.router_en_red[nombre_dispositivo]
            rt.reset()
        else:
            print(f'El router {nombre_dispositivo} no existe en la red. '+
            'Instrucción invalidada!!!')

    def route_add(self, nombre_dispositivo: str, destination: str, mask: str, gateway:str,interface:int) -> None:#---------------claudia---------------
        if self.__contiene__(nombre_dispositivo):
            rt:Router = self.router_en_red[nombre_dispositivo]
            rt.add(destination, mask, gateway, interface)
        else:
            print(f'El router {nombre_dispositivo}no existe en la red. '+
            'Instrucción invalidada!!!')
    
    def route_delete(self, nombre_dispositivo: str, destination: str, mask: str, gateway:str,interface:int) -> None:#---------------claudia---------------
        if self.__contiene__(nombre_dispositivo):
            rt:Router = self.router_en_red[nombre_dispositivo]
            rt.delete(destination, mask, gateway, interface)
        else:
            print(f'El router {nombre_dispositivo}no existe en la red. '+
            'Instrucción invalidada!!!')

    def conectar(self,port1:str,port2:str) -> None:
        """Conecta puerto1 a puerto 2 en caso de ser posible"""
        nombre_dispositivo1 = findall(r'[a-zA-Z0-9]+',port1)[0]
        id_puerto1 = int(findall(r'[1-9]+',port1)[-1])
        nombre_dispositivo2 = findall(r'[a-zA-Z0-9]+',port2)[0]
        id_puerto2 = int(findall(r'[1-9]+',port2)[-1])
        if not self.__contiene__(nombre_dispositivo1) or not self.__contiene__(nombre_dispositivo2):
            print(f'Al menos uno de los dispositivos({nombre_dispositivo1}, {nombre_dispositivo2})'+
            'no se encuentran en la red...Instrucción invalidada!!!')
            return
        if len(self.grafo_red[nombre_dispositivo1]) < id_puerto1:
            print(f'El puerto indicado para el dispositivos({nombre_dispositivo1}'+
            ' no existe...Instrucción invalidada!!!')
            return
        if len(self.grafo_red[nombre_dispositivo2]) < id_puerto2:
            print(f'El puerto indicado para el dispositivos({nombre_dispositivo2}'+
            ' no existe...Instrucción invalidada!!!')
            return
        if self.__crea_ciclo__(dispositivo1=nombre_dispositivo1,dispositivo2=nombre_dispositivo2):
            self.fin_transmision()
            raise Exception('Bucle en la red, configuración no soportada, colapso!!!')
        dispositivo1:Dispositvo = self.__obtener_instancia__(nombre_dispositvo=nombre_dispositivo1)
        dispositivo2:Dispositvo =  self.__obtener_instancia__(nombre_dispositvo=nombre_dispositivo2)
        conectado1 = dispositivo1.esta_conectado(id_puerto1)
        hay_cable_en1 = dispositivo1.tiene_cable(id_puerto1)
        conectado2 = dispositivo2.esta_conectado(id_puerto2)
        hay_cable_en2 = dispositivo2.tiene_cable(id_puerto2)
        if conectado1:
            if not hay_cable_en2:
                dispositivo2.conectar_cable(puerto=id_puerto2)
            print(f'El dispositivos: {nombre_dispositivo1} '+
            'ya esta conectado con algun dispositivo...Instrucción invalidada!!!')
        elif conectado2:
            if not hay_cable_en1:
                dispositivo1.conectar_cable(puerto=id_puerto1)
            print(f'El dispositivos: {nombre_dispositivo1} '+
            'ya esta conectado con algun dispositivo...Instrucción invalidada!!!')
        elif not hay_cable_en1 and not hay_cable_en2:
            dispositivo1.conectar(puerto=id_puerto1)
            dispositivo2.conectar(puerto=id_puerto2)
            self.grafo_red[nombre_dispositivo1][id_puerto1-1] = nombre_dispositivo2
            self.grafo_red[nombre_dispositivo2][id_puerto2-1] = nombre_dispositivo1
        elif hay_cable_en1:
            if not hay_cable_en2:
                dispositivo2.conectar(id_puerto2)
            else:
                print(f'El dispositivos: {nombre_dispositivo2}'+
                'posee un cable en su puerto...Instrucción invalidada!!!')
        else:
            dispositivo1.conectar(id_puerto1)
            print(f'El dispositivos: {nombre_dispositivo2}'+
            'posee un cable en su puerto...Instrucción incompleta!!!')


    def desconectar(self,port:str) -> None:
        """Lleva a cabo la acccion de desconectar el cable del puerto"""
        nombre_dispositivo = findall(r'[a-zA-Z0-9]+',port)[0]
        id_puerto = int(findall(r'[1-9]+',port)[-1])        
        if not self.__contiene__(nombre_dispositivo):
            print(f'El dispositivo: {nombre_dispositivo}, '+
            'no se encuentra en la red...Instrucción invalidada!!!')
            return        
        dispositivo:Dispositvo = self.__obtener_instancia__(nombre_dispositvo=nombre_dispositivo)
        if not dispositivo.tiene_cable(id_puerto):
            return
        if not dispositivo.esta_conectado(id_puerto):
            dispositivo.quitar_cable(id_puerto)
            return
        nombre_dispositivo2 = self.grafo_red[nombre_dispositivo][id_puerto-1]
        dispositivo2:Dispositvo = self.__obtener_instancia__(nombre_dispositvo=nombre_dispositivo2)
        id_puerto2 = self.__puerto_de_A_a_B__(nombre_dispositivo2,nombre_dispositivo)
        self.grafo_red[nombre_dispositivo][id_puerto-1] = None
        self.grafo_red[nombre_dispositivo2][id_puerto2-1] = None
        dispositivo2.desconectar(id_puerto2)
        dispositivo.quitar_cable(id_puerto)


    def __puerto_de_A_a_B__(self,nombre_dispostivo_A:str,nombre_dispositivo_B:str)->int:
        adyacentes_A = self.grafo_red[nombre_dispostivo_A]
        puerto = -1
        for p,dispositivo in enumerate(adyacentes_A):
            if dispositivo == nombre_dispositivo_B:
                puerto = p+1
                break
        return puerto

    def __obtener_instancia__(self,nombre_dispositvo:str)->Dispositvo:
        if self.host_en_red.get(nombre_dispositvo) != None:
            return self.host_en_red[nombre_dispositvo]
        if self.hubs_en_red.get(nombre_dispositvo) != None:
            return self.hubs_en_red[nombre_dispositvo]
        if self.switch_en_red.get(nombre_dispositvo) != None:
            return self.switch_en_red[nombre_dispositvo]
        else:
            return self.router_en_red[nombre_dispositvo]##agreggggue

    def __transmision_bfs_pc__(self,pc:Host,tiempo:int)->None:
        if not pc.estado_transmision(tiempo=tiempo):
            return
        bit = pc.transmitir(tiempo=tiempo)
        pc_nombre = pc.nombre
        nombre_ady =  self.grafo_red[pc_nombre][0]
        if nombre_ady == None:
            return
        disp_adyacente:Dispositvo = self.__obtener_instancia__(nombre_ady)
        cola = []
        visitados = [pc_nombre]
        puerto_ady = self.__puerto_de_A_a_B__(nombre_dispostivo_A=nombre_ady, nombre_dispositivo_B=pc_nombre)
        disp_adyacente.recibir(bit=bit,tiempo=tiempo,puerto=puerto_ady)
        cola.append(disp_adyacente)
        while len(cola) > 0:
            d_hub:Dispositvo = cola.pop(0)
            if d_hub.tipo_dispositivo() != 'hub':
                continue
            for p,nombre_ady in enumerate(self.grafo_red[d_hub.nombre]):
                if nombre_ady != None and not nombre_ady in visitados:
                    disp_adyacente = self.__obtener_instancia__(nombre_dispositvo=nombre_ady)
                    d_hub.transmitir(bit=bit,tiempo=tiempo,puerto=p+1)
                    puerto_ady = self.__puerto_de_A_a_B__(nombre_dispostivo_A=nombre_ady, nombre_dispositivo_B=d_hub.nombre)
                    disp_adyacente.recibir(bit=bit,tiempo=tiempo,puerto=puerto_ady)
                    visitados.append(d_hub.nombre)
                    cola.append(disp_adyacente)

    def __transmision_bfs_switch__(self,switch:Switch,tiempo:int):
        sw_nombre = switch.nombre
        cant_puertos = switch._cantidad_de_puertos
        for p in range(cant_puertos):
            if not switch.estado_transmision(tiempo=tiempo,puerto=p+1):
                continue
            bit = switch.transmitir(tiempo=tiempo,puerto=p+1)
            nombre_ady = self.grafo_red[sw_nombre][p]
            if nombre_ady == None:
                continue
            disp_adyacente:Dispositvo = self.__obtener_instancia__(nombre_ady)
            cola = []
            visitados = [sw_nombre]
            puerto_ady = self.__puerto_de_A_a_B__(nombre_dispostivo_A=nombre_ady, nombre_dispositivo_B=sw_nombre)
            disp_adyacente.recibir(bit=bit,tiempo=tiempo,puerto=puerto_ady)
            cola.append(disp_adyacente)
            while len(cola) > 0:
                hub:Dispositvo = cola.pop(0)
                if hub.tipo_dispositivo() != 'hub':
                    continue
                for p,nombre_ady in enumerate(self.grafo_red[hub.nombre]):
                    if nombre_ady != None and not nombre_ady in visitados:
                        disp_adyacente = self.__obtener_instancia__(nombre_dispositvo=nombre_ady)
                        hub.transmitir(bit=bit,tiempo=tiempo,puerto=p+1)
                        puerto_ady = self.__puerto_de_A_a_B__(nombre_dispostivo_A=nombre_ady, nombre_dispositivo_B=hub.nombre)
                        disp_adyacente.recibir(bit=bit,tiempo=tiempo,puerto=puerto_ady)
                        visitados.append(hub.nombre)
                        cola.append(disp_adyacente)

#####--------------------Agruegue
    def __transmision_bfs_router__(self,router:Router,tiempo:int):
        rt_nombre = router.nombre
        cant_puertos = router._cantidad_de_puertos
        for p in range(cant_puertos):
            if not router.estado_transmision(tiempo=tiempo,puerto=p+1):
                continue
            bit = router.transmitir(tiempo=tiempo,puerto=p+1)
            nombre_ady = self.grafo_red[rt_nombre][p]
            if nombre_ady == None:
                continue
            disp_adyacente:Dispositvo = self.__obtener_instancia__(nombre_ady)
            cola = []
            visitados = [rt_nombre]
            puerto_ady = self.__puerto_de_A_a_B__(nombre_dispostivo_A=nombre_ady, nombre_dispositivo_B=rt_nombre)
            disp_adyacente.recibir(bit=bit,tiempo=tiempo,puerto=puerto_ady)
            cola.append(disp_adyacente)
            while len(cola) > 0:
                hub:Dispositvo = cola.pop(0)
                if hub.tipo_dispositivo() != 'hub':
                    continue
                for p,nombre_ady in enumerate(self.grafo_red[hub.nombre]):
                    if nombre_ady != None and not nombre_ady in visitados:
                        disp_adyacente = self.__obtener_instancia__(nombre_dispositvo=nombre_ady)
                        hub.transmitir(bit=bit,tiempo=tiempo,puerto=p+1)
                        puerto_ady = self.__puerto_de_A_a_B__(nombre_dispostivo_A=nombre_ady, nombre_dispositivo_B=hub.nombre)
                        disp_adyacente.recibir(bit=bit,tiempo=tiempo,puerto=puerto_ady)
                        visitados.append(hub.nombre)
                        cola.append(disp_adyacente)


    def ping(self,tiempo:int, host_name: str, ip_destino: str) -> None: #------------------aqui cambie---------------
        if self.__contiene__(host_name):
            pc = self.host_en_red[host_name]
            #for i in range(4):
            pc.ping(tiempo=tiempo,ip_destino=ip_destino)     
        else:
            print(f'El host {host_name } no existe en la red. '+
            'Instrucción invalidada!!!')

    def transmision(self,tiempo:int):
        for pc in self.host_en_red.values():
            self.__transmision_bfs_pc__(pc=pc,tiempo=tiempo)
        for switch in self.switch_en_red.values():
            self.__transmision_bfs_switch__(switch=switch,tiempo=tiempo)
        for router in self.router_en_red.values():
            self.__transmision_bfs_router__(router=router, tiempo=tiempo)
        for pc in self.host_en_red.values():
            pc.comprobar_estados(tiempo=tiempo)
        for switch in self.switch_en_red.values():
            switch.comprobar_estados(tiempo=tiempo)
        for router in self.router_en_red.values():####----------agregue
            router.comprobar_estados(tiempo=tiempo)
        for hub in self.hubs_en_red.values():
            hub.comprobar_estados(tiempo=tiempo)

    def ordenar_envio_datos_host(self,tiempo:int,host_name:str,datos:str)->None:
        """Le entrega al host sus datos para enviar"""
        if self.host_en_red.get(host_name) == None: # no se encuentra en la red
            print(f'El dispositivo: {host_name}, '+
            'no se encuentra en la red...Instrucción invalidada!!!')
            return
        else:
            pc:Host = self.host_en_red[host_name]
            pc.agragar_datos_envio(tiempo=tiempo,datos=datos)

    def ordenar_envio_trama_host(self,tiempo:int,host_name:str,mac_destino:str,data:str)->None:
        """Le entrega al host la trama para enviar"""
        if self.host_en_red.get(host_name) == None: # no se encuentra en la red
            print(f'El dispositivo: {host_name}, '+
            'no se encuentra en la red...Instrucción invalidada!!!')
            return
        else:
            pc:Host = self.host_en_red[host_name]
            pc.agregar_trama_envio(tiempo=tiempo,mac_destino=mac_destino,data=data)

    def __crea_ciclo__(self,dispositivo1:str, dispositivo2:str)->bool:
        visitados = [dispositivo1]
        cola = [dispositivo1]
        while len(cola) > 0:
            a = cola.pop(0)
            for disp in self.grafo_red[a]:
                if disp != None and not disp in visitados:
                    if disp == dispositivo2:
                        return True
                    else:
                        cola.append(disp)
            visitados.append(a)
        return False

    def fin_transmision(self)->None:
        for host in self.host_en_red.values():
            host.fin_transmision()
        for hub in self.hubs_en_red.values():
            hub.fin_transmision()
        for sw in self.switch_en_red.values():
            sw.fin_transmision()

    def pendientes(self)->bool:
        """Comprueba si quedan envios pendientes en la red"""
        for host in self.host_en_red.values():
            if host.pendiente():
                return True
        for sw in self.switch_en_red.values():
            if sw.pendiente():
                return True       
    
    def ordenar_envio_ip_packet_host(self,tiempo:int,host_name:str,ip_destino:str,data:str)->None:#------------
        if self.host_en_red.get(host_name) == None: # no se encuentra en la red
            print(f'El dispositivo: {host_name}, '+
            'no se encuentra en la red...Instrucción invalidada!!!')
            return
        else:
            pc:Host = self.host_en_red[host_name] 
            pc.agregar_ip_packet(tiempo=tiempo,ip_destino=ip_destino, data=data)
            