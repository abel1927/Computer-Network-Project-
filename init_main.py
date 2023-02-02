from re import findall
from red import Red

def print_grafo_red(red:Red):
    grafo = red.grafo_red
    print(grafo)

def procesar_configuraciones()->list:
    """ Lee las configuraciones en el archivo config.txt, y retorna un
    diccionario con las configuracion: {nombre_config : valor} """
    path='config.txt'
    archivo = open(path,'r')
    configuraciones = []
    for linea in archivo:
        configuraciones.append(linea.split())
    archivo.close()
    dic_config = {'signal_time':10, 'error_detection': 'crc'}
    for line in configuraciones:
        if line[0] == "signal_time":
            dic_config['signal_time'] = int(line[2])
        elif line[0] == 'error_detection':
            dic_config['error_detection'] = line[2]
    return dic_config

def procesar_entrada()->list:
    path='script.txt'
    archivo = open(path,'r')
    instrucciones = []
    for linea in archivo:
        if linea[0].isdigit():
            instrucciones.append(linea.split())
    archivo.close()
    return instrucciones

def procesar_instrucciones(entrada, tiempo)->list:
    temporal = []
    while len(entrada) > 0 and int(entrada[0][0]) == tiempo:
        temporal.append(entrada.pop(0))
    auxiliar = []
    for x in temporal:
        if x[1] == 'create':
            auxiliar.append(x)
    for x in temporal:
        if x[1] == 'mac':
            auxiliar.append(x)
    for x in temporal:
        if x[1] == 'ip':
            auxiliar.append(x)
    for x in temporal:
        if x[1] == 'connect' or x[1] == 'disconnect':
            auxiliar.append(x)
    for x in temporal:
        if x[1] == 'send' or x[1] == 'send_frame' or x[1]=='send_packet':
            auxiliar.append(x)
    for x in temporal:
        if x[1] == 'ping':
            auxiliar.append(x)
    for x in temporal:
        if x[1] == 'route':#---------------claudia---------------
            auxiliar.append(x)
    return auxiliar

def simulador_red():  
    """ Inicia la red y ejecuta toda la simulacion"""
    entrada = procesar_entrada()
    dic_configuraciones = procesar_configuraciones() #diccionario con las configuraciones
    tiempo = 0
    red = Red(dic_configuraciones)
    fin_ejecucion = False
    while not fin_ejecucion:
        instrucciones = procesar_instrucciones(entrada, tiempo)
        while len(instrucciones) > 0:  # mientras haya instrucciones en el ms
            instruccion = instrucciones.pop(0) 
            if instruccion[1] == 'create':
                if instruccion[2] == 'host':
                    red.create_host(instruccion[3])
                elif instruccion[2] == 'hub':
                    red.create_hub(instruccion[3],int(instruccion[4]))
                elif instruccion[2] == 'switch':
                    red.create_switch(instruccion[3],int(instruccion[4]))
                elif instruccion[2] == 'router':#---------------claudia---------------
                    red.create_router(instruccion[3],int(instruccion[4]))
            elif instruccion[1] == 'mac':
                interface = 1
                if ':' in instruccion[2]:
                    interface= int(findall(r'[1-9]+',instruccion[1])[-1])
                red.mac_dispositivo(instruccion[2],instruccion[3], interface=interface)
            elif instruccion[1] == 'ip':
                interface = 1
                if ':' in instruccion[2]:
                    interface = int(findall(r'[1-9]+',instruccion[1])[-1])
                red.ip_dispositvo(instruccion[2], instruccion[3], instruccion[4], interface=interface)
            elif instruccion[1] == 'send':
                red.ordenar_envio_datos_host(tiempo,instruccion[2],instruccion[3])
            elif instruccion[1] == 'send_frame':
                red.ordenar_envio_trama_host(tiempo,instruccion[2],instruccion[3],instruccion[4])
            elif instruccion[1] == 'send_packet':
                red.ordenar_envio_ip_packet_host(tiempo,instruccion[2],instruccion[3],instruccion[4])
            elif instruccion[1] == 'ping':
                red.ping(tiempo,instruccion[2],instruccion[3])   #------------------aqui cambie---------------
            elif instruccion[1] == 'connect':
                red.conectar(instruccion[2],instruccion[3])
            elif instruccion[1] == 'disconnect':
                red.desconectar(instruccion[2])
            elif instruccion[1] == 'route':#---------------claudia---------------
                if instruccion[2] == 'reset':
                    red.route_reset(instruccion[3])
                elif instruccion[2] == 'add':
                    red.route_add(instruccion[3], instruccion[4], instruccion[5], instruccion[6], int(instruccion[7]))
                elif instruccion[2] == 'delete':
                    red.route_delete(instruccion[3], instruccion[4], instruccion[5], instruccion[6], int(instruccion[7]))
        red.transmision(tiempo=tiempo)
        tiempo = tiempo + 1
        if len(entrada) == 0 and tiempo%10==0:    
            fin_ejecucion = not red.pendientes()
    #print(tiempo)
    

if __name__== '__main__':
    simulador_red()