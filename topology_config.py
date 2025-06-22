"""
Configuración de la topología de red y comandos.
"""

# Configuración de routers predefinidos
ROUTERS_CONFIG = [
    ("R1", "172.168.1.1", "admin", "password"),
    ("R2", "172.168.1.2", "admin", "password"),
    ("R3", "172.168.1.6", "admin", "password"),
    ("R4", "172.168.1.10", "admin", "password"),
    ("R5", "172.168.1.21", "admin", "password")
]

# Posiciones de los routers en el canvas
ROUTER_POSITIONS = {
    "R1": (200, 100),
    "R2": (600, 100),
    "R3": (200, 400),
    "R4": (600, 400),
    "R5": (1000, 100)
}

# Conexiones entre routers
CONNECTIONS = [
    ("R1", "R2"),
    ("R1", "R3"),
    ("R2", "R4"),
    ("R2", "R5"),
    ("R3", "R4")
]

# Comandos de consulta predefinidos
QUERY_COMMANDS = {
    "ARP": "show ip arp",
    "ACL": "show access-lists", 
    "DHCP": "show ip dhcp binding",
    "Enrutamiento": "show ip protocols",
    "Interfaces": "show ip interface brief",
    "NAT": "show ip nat translations",
    "QoS": "show policy-map interface",
    "SNMP": "show snmp",
}

# Plantillas de configuración
CONFIG_TEMPLATES = {
    "ACL": [
        "access-list 100 permit ip any any",
        "access-list 100 deny ip any any"
    ],
    "DHCP": [
        "ip dhcp excluded-address 192.168.1.1 192.168.1.10",
        "ip dhcp pool RED_1",
        "network 192.168.1.0 255.255.255.0",
        "default-router 192.168.1.1",
        "dns-server 8.8.8.8",
        "lease 7",
    ],
    "NAT": [
        "access-list 1 permit 192.168.1.0 0.0.0.255",
        "ip nat inside source list 1 interface FastEthernet0/0 overload"
    ],
    "SNMP": [
        "snmp-server community public RO",
        "snmp-server community private RW"
    ],
    "QoS": [
        "class-map match-all VOICE",
        "match ip dscp ef",
        "policy-map QOS_POLICY",
        "class VOICE",
        "priority percent 30"
    ],
    "Enrutamiento": [
        "router ospf 1",
        "network 192.168.1.0 0.0.0.255 area 0"
    ]
}