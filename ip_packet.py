from conversor import Conversor

class IpPacket:
    def __init__(self) -> None:
        self.ip_destino = ''
        self.ip_origen = ''
        self.TTL = '00000000'
        self.Protocolo = '00000000'
        self.tamanho = ''
        self.datos = ''

    def completo_binario(self)->str:
        binario = Conversor.ip_binario(self.ip_destino)
        binario = binario + Conversor.ip_binario(self.ip_origen)
        binario = binario + self.TTL
        binario = binario + self.Protocolo
        binario = binario + self.tamanho
        binario = binario + self.datos
        return binario

    def __str__(self) -> str:
        a = f"""ip_destino:{self.ip_destino}
        ip_origen:{self.ip_origen}
        TTL:{self.TTL}
        Protocolo:{self.Protocolo}
        tamanho:{self.tamanho}
        datos:{self.datos}"""
        return a

    #def agregar_ip_origen(self, ip_origen:str)->None:
    #    self.ip_origen = ip_origen


def crear_ip_packet(ip_destino:str, ip_origen:str, data:str)->IpPacket:
        packet = IpPacket()
        packet.ip_destino = ip_destino
        packet.ip_origen = ip_origen
        packet.datos = Conversor.hexadecimal_binario(data)
        packet.tamanho = Conversor.decimal_binario(len(data)//2)
        return packet

def crear_ip_packet2(packet_binario:str)->IpPacket:
    packet = IpPacket()
    packet.ip_destino = Conversor.binario_ip(packet_binario[0:32])
    packet.ip_origen = Conversor.binario_ip(packet_binario[32:64])
    packet.TTL = packet_binario[64:72]
    packet.Protocolo = packet_binario[72:80]
    packet.tamanho = packet_binario[80:88]
    packet.datos = Conversor.binario_hexadecimal(packet_binario[88:])
    return packet

def crear_ip_packet_icmp(ip_destino:str, ip_origen:str,)->IpPacket:
    packet = IpPacket()
    packet.ip_destino = ip_destino
    packet.ip_origen = ip_origen
    packet.Protocolo = '00000001'
    packet.tamanho = '00000001'
    return packet


def crear_ip_packet_pong(ip_destino:str, ip_origen:str)->IpPacket:
    packet = crear_ip_packet_icmp(ip_destino, ip_origen)
    packet.datos = '00000000'
    return packet

def crear_ip_packet_destination_host_unreachable(ip_destino:str, ip_origen:str)->IpPacket:
    packet = crear_ip_packet_icmp(ip_destino, ip_origen)
    packet.datos = '00000011'
    return packet

def crear_ip_packet_ping(ip_destino:str, ip_origen:str)->IpPacket:
    packet = crear_ip_packet_icmp(ip_destino, ip_origen)
    packet.datos = '00001000'
    return packet

def crear_ip_packet_time_exceeded(ip_destino:str, ip_origen:str)->IpPacket:
    packet = crear_ip_packet_icmp(ip_destino, ip_origen)
    packet.datos = '00001011'
    return packet


def is_ping_packet(ipPacket:IpPacket)->bool:
    return (ipPacket.Protocolo == '00000001' and ipPacket.datos == '00001000')