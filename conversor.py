from re import findall
class Conversor:

    @staticmethod
    def decimal_binario(decimal:int,numero_bits=8)->str:
        b = bin(decimal)
        b2 = b[2:]
        if len(b2) == numero_bits:
            return str(b2)
        else:
            dif = numero_bits-len(b2)
            return '0'*dif + b2

    @staticmethod
    def hexadecimal_binario(hexa:str)->str:
        dic_hex_bin={'0':'0000','1':'0001','2':'0010','3':'0011','4':'0100','5':'0101',
        '6':'0110','7':'0111','8':'1000','9':'1001','A':'1010','B':'1011',
        'C':'1100','D':'1101','E':'1110','F':'1111'}
        binario=[]
        for i in hexa:
            binario.append(dic_hex_bin[i])
        binario_final= "".join(binario)
        return binario_final

    @staticmethod
    def binario_hexadecimal(binario:str)->str:
        dic_bin_hex  = {'0000': '0', '0001': '1', '0010': '2', '0011': '3', '0100': '4', '0101': '5',
            '0110': '6', '0111': '7', '1000': '8', '1001': '9', '1010': 'A', '1011': 'B',
            '1100': 'C', '1101': 'D', '1110': 'E', '1111': 'F'}
        hexa = ""
        i = 0
        while i <= len(binario)-4:
            b = ""
            for j in range(4):
                b = b+binario[i+j]
            hexa = hexa + dic_bin_hex[b]
            i = i+4
        return hexa

    @staticmethod
    def ip_hexadecimal(ip:str):
        numeros = findall(r'[0-9]+', ip)
        binario = ''
        for n in numeros:
            binario = binario + Conversor.decimal_binario(int(n))
        return binario,Conversor.binario_hexadecimal(binario)

    @staticmethod
    def binario_ip(binario:str):
        ip = ''
        binarios =  [binario[0:8], binario[8:16], binario[16:24], binario[24:32]]
        for i in range(4):
            decimal = 0
            for posicion, digito in enumerate(binarios[i][::-1]):
                decimal = decimal + int(digito) * 2 ** posicion
            ip = ip + str(decimal)
            if i != 3:
                ip = ip + '.'
        return ip

    @staticmethod	
    def ip_binario(ip:str):
        numeros = findall(r'[0-9]+', ip)
        binario = ''
        for n in numeros:
            binario = binario + Conversor.decimal_binario(int(n))
        return binario

    @staticmethod	
    def binario_decimal(binario:str): #------------------aqui cambie---------------
        decimal = 0 

        for posicion, digito_string in enumerate(binario[::-1]):
            decimal += int(digito_string) * 2 ** posicion

        return decimal

