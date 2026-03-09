from scapy.all import ARP, Ether, srp

def scan_network(ip_range):
    #1. Criando um pacote ARP pedindo "Quem tem esse IP?"
    arp = ARP(pdst=ip_range)
    
    #2. Criando um pacote Ethernet para envciar em broadcast
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    
    #3. Unindo os pacotes
    pacote = ether/arp
    
    #4. Enviamos e recebendo as respostas
    resultado = srp(pacote, timeout=2, verbose=False)[0]
    
    dispositivos = []
    for enviado, recebido in resultado:
        #Adicionando cada dispositivo recente a lista
        dispositivos.append({'ip': recebido.psrc, 'mac': recebido.hwsrc})
          
    return dispositivos