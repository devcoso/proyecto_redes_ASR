import tkinter as tk
from tkinter import ttk, messagebox

class RouterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Router Manager - Administración de Red")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Variables para almacenar datos
        self.routers_data = {
            "R1": {"ip": "192.168.1.1", "estado": "Desconectado"},
            "R2": {"ip": "192.168.2.1", "estado": "Desconectado"},
            "R3": {"ip": "192.168.3.1", "estado": "Desconectado"},
            "R4": {"ip": "192.168.4.1", "estado": "Desconectado"},
            "R5": {"ip": "172.168.1.21", "estado": "Desconectado"}
        }
        
        self.router_seleccionado = None
        
        self.crear_interfaz()
        
    def crear_interfaz(self):
        """Crea la interfaz gráfica completa"""
        
        # Frame principal con padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar expansión
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # TÍTULO PRINCIPAL
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        title_label = ttk.Label(title_frame, text="🌐 Router Manager", 
                               font=("Arial", 20, "bold"))
        title_label.pack(side=tk.LEFT)
        
        # Botones de control general
        control_frame = ttk.Frame(title_frame)
        control_frame.pack(side=tk.RIGHT)
        
        self.btn_conectar_todos = ttk.Button(control_frame, text="🔌 Conectar Todos")
        self.btn_conectar_todos.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_desconectar_todos = ttk.Button(control_frame, text="🔌 Desconectar Todos")
        self.btn_desconectar_todos.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_actualizar = ttk.Button(control_frame, text="🔄 Actualizar")
        self.btn_actualizar.pack(side=tk.LEFT)
        
        # FRAME IZQUIERDO - Lista de Routers
        left_frame = ttk.LabelFrame(main_frame, text="📋 Lista de Routers", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        
        # Frame para controles de router individual
        router_controls = ttk.Frame(left_frame)
        router_controls.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.btn_conectar_ind = ttk.Button(router_controls, text="🔌 Conectar")
        self.btn_conectar_ind.pack(side=tk.LEFT, padx=(0, 5))
        
        self.btn_desconectar_ind = ttk.Button(router_controls, text="❌ Desconectar")
        self.btn_desconectar_ind.pack(side=tk.LEFT, padx=(0, 5))
        
        self.label_seleccionado = ttk.Label(router_controls, text="Router: Ninguno", 
                                           font=("Arial", 10, "italic"))
        self.label_seleccionado.pack(side=tk.RIGHT)
        
        # Listbox para routers
        self.listbox_routers = tk.Listbox(left_frame, font=("Consolas", 11), 
                                         selectmode=tk.SINGLE, height=15)
        self.listbox_routers.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.listbox_routers.bind('<<ListboxSelect>>', self.on_router_select)
        
        # Scrollbar para listbox
        scrollbar_routers = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, 
                                         command=self.listbox_routers.yview)
        scrollbar_routers.grid(row=1, column=1, sticky=(tk.N, tk.S))
        self.listbox_routers.configure(yscrollcommand=scrollbar_routers.set)
        
        # FRAME DERECHO - Opciones y Contenido
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Panel de opciones
        self.crear_panel_opciones(right_frame)
        
        # Panel de contenido
        self.crear_panel_contenido(right_frame)
        
        # Cargar routers en la lista
        self.actualizar_lista_routers()
        
    def crear_panel_opciones(self, parent):
        """Crea el panel de opciones para el router seleccionado"""
        options_frame = ttk.LabelFrame(parent, text="🔧 Opciones del Router", padding="10")
        options_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        options_frame.columnconfigure(0, weight=1)
        
        # Frame para botones principales
        main_options = ttk.Frame(options_frame)
        main_options.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botones principales
        self.btn_informacion = ttk.Button(main_options, text="📊 1. Información", 
                                         command=lambda: self.mostrar_opcion("Información"))
        self.btn_informacion.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_enrutamiento = ttk.Button(main_options, text="🛣️ 2. Enrutamiento", 
                                          command=lambda: self.mostrar_opcion("Enrutamiento"))
        self.btn_enrutamiento.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_pcs = ttk.Button(main_options, text="💻 3. PCs Conectadas", 
                                 command=lambda: self.mostrar_opcion("PCs Conectadas"))
        self.btn_pcs.pack(side=tk.LEFT, padx=(0, 10))
        
        # Separador
        separator = ttk.Separator(options_frame, orient='horizontal')
        separator.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Label para servicios
        services_label = ttk.Label(options_frame, text="🔍 Mostrar Servicios:", 
                                  font=("Arial", 11, "bold"))
        services_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        
        # Frame para servicios
        services_frame = ttk.Frame(options_frame)
        services_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
        # Botones de servicios - Primera fila
        services_row1 = ttk.Frame(services_frame)
        services_row1.pack(fill=tk.X, pady=(0, 5))
        
        self.btn_acl = ttk.Button(services_row1, text="🛡️ ACL", 
                                 command=lambda: self.mostrar_opcion("ACL"))
        self.btn_acl.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_dhcp = ttk.Button(services_row1, text="🌐 DHCP", 
                                  command=lambda: self.mostrar_opcion("DHCP"))
        self.btn_dhcp.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_nat = ttk.Button(services_row1, text="🔄 NAT", 
                                 command=lambda: self.mostrar_opcion("NAT"))
        self.btn_nat.pack(side=tk.LEFT, padx=(0, 10))
        
        # Segunda fila
        services_row2 = ttk.Frame(services_frame)
        services_row2.pack(fill=tk.X)
        
        self.btn_dns = ttk.Button(services_row2, text="🌍 DNS", 
                                 command=lambda: self.mostrar_opcion("DNS"))
        self.btn_dns.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_vpn = ttk.Button(services_row2, text="🔐 VPN", 
                                 command=lambda: self.mostrar_opcion("VPN"))
        self.btn_vpn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Inicialmente deshabilitar botones
        self.deshabilitar_opciones()
        
    def crear_panel_contenido(self, parent):
        """Crea el panel donde se muestra el contenido"""
        content_frame = ttk.LabelFrame(parent, text="📄 Contenido", padding="10")
        content_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Notebook para pestañas
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Pestaña de bienvenida
        welcome_frame = ttk.Frame(self.notebook)
        self.notebook.add(welcome_frame, text="🏠 Inicio")
        
        welcome_label = ttk.Label(welcome_frame, 
                                 text="👋 Bienvenido al Router Manager\n\n"
                                      "📌 Instrucciones:\n"
                                      "1. Selecciona un router de la lista\n"
                                      "2. Conecta al router\n"
                                      "3. Explora las opciones disponibles\n\n"
                                      "🔧 Funciones disponibles:\n"
                                      "• Información del dispositivo\n"
                                      "• Configuración de enrutamiento\n"
                                      "• Dispositivos conectados\n"
                                      "• Servicios de red (ACL, DHCP, NAT, DNS, VPN)",
                                 font=("Arial", 12), justify=tk.LEFT)
        welcome_label.pack(expand=True)
        
    def actualizar_lista_routers(self):
        """Actualiza la lista de routers en el listbox"""
        self.listbox_routers.delete(0, tk.END)
        
        for nombre, datos in self.routers_data.items():
            estado_icon = "🟢" if datos["estado"] == "Conectado" else "🔴"
            item = f"{estado_icon} {nombre} ({datos['ip']}) - {datos['estado']}"
            self.listbox_routers.insert(tk.END, item)
    
    def on_router_select(self, event):
        """Maneja la selección de un router"""
        selection = self.listbox_routers.curselection()
        if selection:
            index = selection[0]
            router_names = list(self.routers_data.keys())
            self.router_seleccionado = router_names[index]
            
            # Actualizar label
            router_data = self.routers_data[self.router_seleccionado]
            self.label_seleccionado.config(
                text=f"Router: {self.router_seleccionado} ({router_data['ip']})"
            )
            
            # Habilitar/deshabilitar botones según estado
            if router_data["estado"] == "Conectado":
                self.habilitar_opciones()
            else:
                self.deshabilitar_opciones()
    
    def habilitar_opciones(self):
        """Habilita los botones de opciones"""
        botones = [self.btn_informacion, self.btn_enrutamiento, self.btn_pcs,
                  self.btn_acl, self.btn_dhcp, self.btn_nat, self.btn_dns, self.btn_vpn]
        
        for btn in botones:
            btn.configure(state='normal')
    
    def deshabilitar_opciones(self):
        """Deshabilita los botones de opciones"""
        botones = [self.btn_informacion, self.btn_enrutamiento, self.btn_pcs,
                  self.btn_acl, self.btn_dhcp, self.btn_nat, self.btn_dns, self.btn_vpn]
        
        for btn in botones:
            btn.configure(state='disabled')
    
    def mostrar_opcion(self, opcion):
        """Muestra el contenido de la opción seleccionada"""
        if not self.router_seleccionado:
            messagebox.showwarning("Sin selección", "Por favor selecciona un router primero.")
            return
        
        # Crear nueva pestaña o actualizar existente
        tab_name = f"📋 {opcion}"
        
        # Buscar si ya existe la pestaña
        tab_exists = False
        for i in range(self.notebook.index("end")):
            if self.notebook.tab(i, "text") == tab_name:
                self.notebook.select(i)
                tab_exists = True
                break
        
        if not tab_exists:
            # Crear nueva pestaña
            new_frame = ttk.Frame(self.notebook)
            self.notebook.add(new_frame, text=tab_name)
            self.notebook.select(new_frame)
            
            # Contenido placeholder
            self.crear_contenido_opcion(new_frame, opcion)
    
    def crear_contenido_opcion(self, parent, opcion):
        """Crea el contenido para cada opción"""
        # Frame principal con scroll
        canvas = tk.Canvas(parent, bg='white')
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Título de la sección
        title_label = ttk.Label(scrollable_frame, 
                               text=f"🔍 {opcion} - {self.router_seleccionado}",
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Contenido específico según la opción
        content_text = self.obtener_contenido_placeholder(opcion)
        
        content_label = ttk.Label(scrollable_frame, text=content_text, 
                                 font=("Consolas", 10), justify=tk.LEFT,
                                 background='white', relief='sunken', 
                                 padding=20)
        content_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Botón de actualizar
        btn_refresh = ttk.Button(scrollable_frame, text="🔄 Actualizar Información",
                                command=lambda: self.actualizar_contenido(opcion))
        btn_refresh.pack(pady=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def obtener_contenido_placeholder(self, opcion):
        """Retorna contenido placeholder para cada opción"""
        placeholders = {
            "Información": """
🔧 INFORMACIÓN DEL ROUTER
═══════════════════════════════════════

📊 Estado del Sistema:
    • Hostname: [PLACEHOLDER]
    • Versión IOS: [PLACEHOLDER]
    • Uptime: [PLACEHOLDER]
    • Memoria RAM: [PLACEHOLDER]
    • CPU: [PLACEHOLDER]

🌐 Interfaces de Red:
    • GigabitEthernet0/0: [PLACEHOLDER]
    • GigabitEthernet0/1: [PLACEHOLDER]
    • Serial0/0/0: [PLACEHOLDER]

⚙️ Configuración Básica:
    • Enable Secret: [CONFIGURADO]
    • Console Password: [CONFIGURADO]
    • VTY Lines: [CONFIGURADO]
            """,
            
            "Enrutamiento": """
🛣️ TABLA DE ENRUTAMIENTO
═══════════════════════════════════════

📋 Rutas Activas:
    C    192.168.1.0/24 conectada, GigabitEthernet0/0
    C    192.168.2.0/24 conectada, GigabitEthernet0/1
    S    0.0.0.0/0 [1/0] via 10.0.0.1
    
🔄 Protocolos de Enrutamiento:
    • OSPF: [ESTADO - PLACEHOLDER]
        - Process ID: [PLACEHOLDER]
        - Router ID: [PLACEHOLDER]
        - Areas: [PLACEHOLDER]
    
    • EIGRP: [ESTADO - PLACEHOLDER]
        - AS Number: [PLACEHOLDER]
        - Neighbors: [PLACEHOLDER]
    
    • RIP: [ESTADO - PLACEHOLDER]
        - Version: [PLACEHOLDER]
        - Networks: [PLACEHOLDER]
            """,
            
            "PCs Conectadas": """
💻 DISPOSITIVOS CONECTADOS
═══════════════════════════════════════

🖥️ Tabla ARP:
    192.168.1.10    00:1B:44:11:3A:B7    GigabitEthernet0/0
    192.168.1.15    00:50:56:C0:00:01    GigabitEthernet0/0
    192.168.2.20    00:0C:29:68:4C:A5    GigabitEthernet0/1
    
📊 Estadísticas de Tráfico:
    • Total dispositivos: [PLACEHOLDER]
    • Activos en última hora: [PLACEHOLDER]
    • Tráfico entrante: [PLACEHOLDER]
    • Tráfico saliente: [PLACEHOLDER]

🔍 DHCP Leases Activos:
    • 192.168.1.100 - PC-Workstation-01
    • 192.168.1.101 - Laptop-Usuario-02
    • 192.168.1.102 - Impresora-Oficina
            """,
            
            "ACL": """
🛡️ ACCESS CONTROL LISTS (ACL)
═══════════════════════════════════════

📋 ACLs Estándar:
    access-list 10 permit 192.168.1.0 0.0.0.255
    access-list 10 deny any
    
📋 ACLs Extendidas:
    access-list 100 permit tcp 192.168.1.0 0.0.0.255 any eq 80
    access-list 100 permit tcp 192.168.1.0 0.0.0.255 any eq 443
    access-list 100 deny ip any any
    
🔧 ACLs Aplicadas:
    • GigabitEthernet0/0 (in): access-group 10
    • GigabitEthernet0/1 (out): access-group 100
    
📊 Estadísticas de ACL:
    • Paquetes permitidos: [PLACEHOLDER]
    • Paquetes denegados: [PLACEHOLDER]
            """,
            
            "DHCP": """
🌐 DYNAMIC HOST CONFIGURATION PROTOCOL
═══════════════════════════════════════

⚙️ Configuración DHCP:
    ip dhcp pool LAN1
        network 192.168.1.0 255.255.255.0
        default-router 192.168.1.1
        dns-server 8.8.8.8 8.8.4.4
        lease 7
    
📊 Estado del Servicio:
    • DHCP Server: [ACTIVO/INACTIVO]
    • Pool Activos: [PLACEHOLDER]
    • Direcciones Asignadas: [PLACEHOLDER]
    • Direcciones Disponibles: [PLACEHOLDER]

📋 Leases Activos:
    IP Address      MAC Address         Lease Expiration
    192.168.1.100   00:1B:44:11:3A:B7   23:45:12
    192.168.1.101   00:50:56:C0:00:01   22:30:45
            """,
            
            "NAT": """
🔄 NETWORK ADDRESS TRANSLATION
═══════════════════════════════════════

⚙️ Configuración NAT:
    interface GigabitEthernet0/0
        ip nat inside
    
    interface GigabitEthernet0/1
        ip nat outside
    
    ip nat inside source list 1 interface GigabitEthernet0/1 overload
    
📊 Traducciones Activas:
    Inside Local    Inside Global     Outside Local   Outside Global
    192.168.1.10    203.0.113.5:1024  198.51.100.1:80 198.51.100.1:80
    192.168.1.15    203.0.113.5:1025  8.8.8.8:53      8.8.8.8:53
    
📈 Estadísticas NAT:
    • Traducciones totales: [PLACEHOLDER]
    • Traducciones activas: [PLACEHOLDER]
    • Pool utilization: [PLACEHOLDER]%
            """,
            
            "DNS": """
🌍 DOMAIN NAME SYSTEM
═══════════════════════════════════════

⚙️ Configuración DNS:
    ip domain-name empresa.local
    ip name-server 8.8.8.8
    ip name-server 8.8.4.4
    ip domain-lookup
    
📊 Cache DNS:
    Host                    Address(es)
    google.com              142.250.184.14
    cloudflare.com          104.16.132.229
    empresa.local           192.168.1.1
    
🔍 Consultas Recientes:
    • google.com: Resuelto - 142.250.184.14
    • facebook.com: Resuelto - 157.240.12.35
    • empresa.local: Resuelto - 192.168.1.1
    
📈 Estadísticas DNS:
    • Consultas exitosas: [PLACEHOLDER]
    • Consultas fallidas: [PLACEHOLDER]
    • Cache hits: [PLACEHOLDER]
            """,
            
            "VPN": """
🔐 VIRTUAL PRIVATE NETWORK
═══════════════════════════════════════

⚙️ Túneles VPN Configurados:
    IPSec Tunnel 1:
        • Destino: 203.0.113.10
        • Estado: UP
        • Protocolo: ESP
        • Encriptación: AES-256
    
    IPSec Tunnel 2:
        • Destino: 198.51.100.20
        • Estado: DOWN
        • Protocolo: ESP
        • Encriptación: 3DES
    
📊 Estadísticas VPN:
    • Túneles activos: 1 de 2
    • Tráfico encriptado: [PLACEHOLDER] MB
    • Paquetes transmitidos: [PLACEHOLDER]
    • Errores de autenticación: 0
    
🔑 Certificados:
    • CA Certificate: VÁLIDO (Exp: 2025-12-31)
    • Local Certificate: VÁLIDO (Exp: 2024-12-31)
            """
        }
        
        return placeholders.get(opcion, f"Contenido para {opcion} no disponible")
    
    def actualizar_contenido(self, opcion):
        """Placeholder para actualizar contenido"""
        messagebox.showinfo("Actualizar", f"Actualizando información de {opcion}...")
        # Aquí iría la lógica real para obtener datos del router


def main():
    root = tk.Tk()
    app = RouterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()