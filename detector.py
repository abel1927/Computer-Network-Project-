
class CRC:

    @staticmethod
    def codificar_trama_crc(datos:list)->tuple:
        """Retorna una tupla con el string del tamaño de verificacion y
        el string de los bits de verificacion"""
        #x16 + x12 + x5 + 1. 
        G = [1,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,1]
        datos_calculo = datos.copy()
        datos_calculo.extend([0]*16)
        for i in range(len(datos_calculo)-16):
            if datos_calculo[i] == 0: continue
            for j in range(17):
                datos_calculo[i+j] = datos_calculo[i+j]^G[j]
        resto = datos_calculo[len(datos_calculo)-16:]
        tamanho = '0'*6 +'10'
        r = "".join(map(str,resto))
        return (tamanho,r)

    @staticmethod
    def decodificar_trama_crc(datos_mas_verifcacion:list)->bool:
        """Retorna True si los datos son correctos"""
        G = [1,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,1]
        for i in range(len(datos_mas_verifcacion)-16):
            if datos_mas_verifcacion[i] == 0: continue
            for j in range(17):
                datos_mas_verifcacion[i+j] = datos_mas_verifcacion[i+j]^G[j]
        resto = datos_mas_verifcacion[len(datos_mas_verifcacion)-16:]
        return not 1 in resto

class Hamming:
    @staticmethod
    def codificar_trama_hamming(datos:list)->tuple:
        data=list(datos)
        c,ch,j,r,h = 0,0,0,0,[]

        while ((len(data)+r+1) > (pow(2,r))):
            r=r+1

        for i in range(0,(r+len(data))):
            p = (2**c)

            if(p==(i+1)):
                h.append(0)
                c = c+1
            else:
                h.append(int(data[j]))
                j = j+1

        for parity in range(0,(len(h))):
            ph = (2**ch)
            if(ph == (parity+1)):
                startIndex = ph-1
                i = startIndex
                parity_bit = []

                while(i<len(h)):
                    block=h[i:i+ph]
                    parity_bit.extend(block)
                    i+=2*ph

                for z in range(1,len(parity_bit)):
                    h[startIndex]=h[startIndex]^parity_bit[z]
                ch+=1
        result=list(h)
        while(len(result)%8 != 0):
            result.append(0)
        tamanho = str(int(len(result)/8))
        r ="".join(map(str,result))
        return (tamanho, r)
    
    @staticmethod
    def decodificar_trama_hamming(datos, bits_de_verifcacion)->bool:

        data=list(datos)
        c,ch,j,r,h=0,0,0,0,[]

        while ((len(data)+r+1)>(pow(2,r))):
            r=r+1

        for i in range(0,(r+len(data))):
            p=(2**c)

            if(p==(i+1)):
                h.append(0)
                c=c+1

            else:
                h.append(int(data[j]))
                j=j+1

        for parity in range(0,(len(h))):
            ph=(2**ch)
            if(ph==(parity+1)):
                startIndex=ph-1
                i=startIndex
                parity_bit=[]

                while(i<len(h)):
                    block=h[i:i+ph]
                    parity_bit.extend(block)
                    i+=2*ph

                for z in range(1,len(parity_bit)):
                    h[startIndex]=h[startIndex]^parity_bit[z]
                ch+=1
        result=list(h)
        while(len(result)%8 != 0):
            result.append(0)

        if(len(bits_de_verifcacion) != len(result)):
            return True

        p1,c1=1,0
        for i in range(1,r):  
            p1=p1**r
            if(bits_de_verifcacion[p1-1]!=result[p1-1]):
                    return True       
        return False