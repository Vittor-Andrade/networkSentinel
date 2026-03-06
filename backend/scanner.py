from scapy.all import ARP, Ether, srp, conf

def scan_network(ip_range):
    print(f"Escaner iniciando na rede: {ip_range}")
    
    # Criando o pacote
    arp_request = ARP(pdst=ip_range)
    broadcast = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = broadcast / arp_request
    
    # No Windows, às vezes precisamos definir a interface explicitamente
    # result = srp(packet, timeout=3, verbose=False, iface=conf.iface)[0]
    
    # Tentativa padrão com timeout maior (3 segundos)
    result = srp(packet, timeout=3, verbose=False)[0]
    
    devices = []
    for sent, received in result:
        # Debug no console do Python para você ver se o MAC está chegando aqui
        print(f"Encontrado: IP {received.psrc} - MAC {received.hwsrc}")
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})
        
    return devices