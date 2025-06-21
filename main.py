import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from router_ssh import RouterManager

class RouterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Router Manager - Administración de Red")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Manager de routers
        self.manager = RouterManager()
        
        # Variables para el estado
        self.router_seleccionado = None
        self.actualizar_activo = False
        self.thread_actualizacion = None
        
        # Configuración de routers
        self.routers_config = {
            "R1": {"ip": "192.168.1.1", "usuario": "admin", "password": "password"},
            "R2": {"ip": "192.168.2.1", "usuario": "admin", "password": "password"},
            "R3": {"ip": "192.168.3.1", "usuario": "admin", "password": "password"},
            "R4": {"ip": "192.168.4.1", "usuario": "admin", "password": "password"},
            "R5": {"ip": "172.168.1.21", "usuario": "admin", "password": "password"}
        }
        
        self.crear_interfaz()
        self.inicializar_routers()
        
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
        
        self.btn_conectar_todos = ttk.Button(control_frame, text="🔌 Conectar Todos",
                                           command=self.conectar_todos)
        self.btn_conectar_todos.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_desconectar_todos = ttk.Button(control_frame, text="🔌 Desconectar Todos",
                                              command=self.desconectar_todos)
        self.btn_desconectar_todos.pack(side=tk.LEFT, padx=(0, 10))
        
        self.btn_actualizar = ttk.Button(control_frame, text="🔄 Actualizar",
                                       command=self.actualizar_lista_routers)
        self.btn_actualizar.pack(side=tk.LEFT)
        
        # Checkbox para auto-actualización
        self.auto_update_var = tk.BooleanVar()
        self.checkbox_auto = ttk.Checkbutton(control_frame, text="Auto-actualizar (5s)", 
                                           variable=self.auto_update_var,
                                           command=self.toggle_auto_update)
        self.checkbox_auto.pack(side=tk.LEFT, padx=(10, 0))
        
        # FRAME IZQUIERDO - Lista de Routers
        left_frame = ttk.LabelFrame(main_frame, text="📋 Lista de Routers", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(1, weight=1)
        
        # Frame para controles de router individual
        router_controls = ttk.Frame(left_frame)
        router_controls.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.btn_conectar_ind = ttk.Button(router_controls, text="🔌 Conectar",
                                         command=self.conectar_seleccionado)
        self.btn_conectar_ind.pack(side=tk.LEFT, padx=(0, 5))
        
        self.btn_desconectar_ind = ttk.Button(router_controls, text="❌ Desconectar",
                                            command=self.desconectar_seleccionado)
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
        
    def inicializar_routers(self):
        """Inicializa los routers en el manager"""
        for nombre, config in self.routers_config.items():
            self.manager.agregar_router(
                nombre, 
                config["ip"], 
                config["usuario"], 
                config["password"]
            )
        self.actualizar_lista_routers()
    
    def actualizar_lista_routers(self):
        """Actualiza la lista de routers en el listbox"""
        self.listbox_routers.delete(0, tk.END)
        
        for nombre, router in self.manager.routers.items():
            estado_info = router.obtener_estado()
            estado_icon = "🟢" if estado_info["conectado"] else "🔴"
            estado_text = "Conectado" if estado_info["conectado"] else "Desconectado"
            
            item = f"{estado_icon} {nombre} ({estado_info['ip']}) - {estado_text}"
            self.listbox_routers.insert(tk.END, item)
    
    def on_router_select(self, event):
        """Maneja la selección de un router"""
        selection = self.listbox_routers.curselection()
        if selection:
            index = selection[0]
            router_names = list(self.manager.routers.keys())
            self.router_seleccionado = router_names[index]
            
            # Obtener router del manager
            router = self.manager.obtener_router(self.router_seleccionado)
            
            # Actualizar label
            self.label_seleccionado.config(
                text=f"Router: {self.router_seleccionado} ({router.ip})"
            )
            
            # Habilitar/deshabilitar botones según estado
            if router.conectado:
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
    
    def conectar_todos(self):
        """Conecta a todos los routers en un hilo separado"""
        def conectar():
            self.btn_conectar_todos.configure(state='disabled')
            try:
                resultados = self.manager.conectar_todos()
                
                # Actualizar interfaz en el hilo principal
                self.root.after(0, lambda: self.actualizar_lista_routers())
                self.root.after(0, lambda: self.mostrar_resultado_conexion(resultados))
            finally:
                self.root.after(0, lambda: self.btn_conectar_todos.configure(state='normal'))
        
        threading.Thread(target=conectar, daemon=True).start()
    
    def desconectar_todos(self):
        """Desconecta todos los routers"""
        self.manager.desconectar_todos()
        self.actualizar_lista_routers()
        self.deshabilitar_opciones()
        messagebox.showinfo("Desconexión", "Todos los routers desconectados.")
    
    def conectar_seleccionado(self):
        """Conecta el router seleccionado"""
        if not self.router_seleccionado:
            messagebox.showwarning("Sin selección", "Por favor selecciona un router primero.")
            return
        
        router = self.manager.obtener_router(self.router_seleccionado)
        
        def conectar():
            self.btn_conectar_ind.configure(state='disabled')
            try:
                if router.conectar():
                    self.root.after(0, lambda: messagebox.showinfo("Conexión", 
                                    f"✓ Conexión exitosa a {router.nombre}"))
                    self.root.after(0, self.habilitar_opciones)
                else:
                    self.root.after(0, lambda: messagebox.showerror("Error", 
                                    f"✗ Error conectando a {router.nombre}"))
            finally:
                self.root.after(0, lambda: self.actualizar_lista_routers())
                self.root.after(0, lambda: self.btn_conectar_ind.configure(state='normal'))
        
        threading.Thread(target=conectar, daemon=True).start()
    
    def desconectar_seleccionado(self):
        """Desconecta el router seleccionado"""
        if not self.router_seleccionado:
            messagebox.showwarning("Sin selección", "Por favor selecciona un router primero.")
            return
        
        router = self.manager.obtener_router(self.router_seleccionado)
        router.desconectar()
        self.actualizar_lista_routers()
        self.deshabilitar_opciones()
        messagebox.showinfo("Desconexión", f"Router {router.nombre} desconectado.")
    
    def mostrar_resultado_conexion(self, resultados):
        """Muestra el resultado de las conexiones"""
        mensaje = "Resultados de conexión:\n\n"
        for nombre, exito in resultados.items():
            estado = "✓ Éxito" if exito else "✗ Falló"
            mensaje += f"{nombre}: {estado}\n"
        
        messagebox.showinfo("Conexiones", mensaje)
    
    def mostrar_opcion(self, opcion):
        """Muestra el contenido de la opción seleccionada"""
        if not self.router_seleccionado:
            messagebox.showwarning("Sin selección", "Por favor selecciona un router primero.")
            return
        
        router = self.manager.obtener_router(self.router_seleccionado)
        if not router.conectado:
            messagebox.showwarning("Router Desconectado", 
                                 f"El router {router.nombre} no está conectado.")
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
            
            # Crear contenido
            self.crear_contenido_opcion(new_frame, opcion, router)
        else:
            # Actualizar contenido existente
            self.actualizar_contenido_existente(opcion, router)
    
    def crear_contenido_opcion(self, parent, opcion, router):
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
                               text=f"🔍 {opcion} - {router.nombre}",
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=10)
        
        # Área de texto para contenido
        text_widget = tk.Text(scrollable_frame, font=("Consolas", 10), 
                             wrap=tk.WORD, height=25, width=80,
                             background='white', relief='sunken')
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Scrollbar para el texto
        text_scrollbar = ttk.Scrollbar(scrollable_frame, orient=tk.VERTICAL, 
                                      command=text_widget.yview)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        text_widget.configure(yscrollcommand=text_scrollbar.set)
        
        # Botón de actualizar
        btn_refresh = ttk.Button(scrollable_frame, text="🔄 Actualizar Información",
                                command=lambda: self.actualizar_contenido_real(opcion, router, text_widget))
        btn_refresh.pack(pady=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Cargar contenido inicial
        self.actualizar_contenido_real(opcion, router, text_widget)
    
    def actualizar_contenido_real(self, opcion, router, text_widget):
        """Actualiza el contenido real obteniendo datos del router"""
        def obtener_datos():
            text_widget.delete(1.0, tk.END)
            text_widget.insert(tk.END, f"🔄 Obteniendo {opcion} de {router.nombre}...\n\n")
            
            try:
                if opcion == "Información":
                    self.obtener_informacion(router, text_widget)
                elif opcion == "Enrutamiento":
                    self.obtener_enrutamiento(router, text_widget)
                elif opcion == "PCs Conectadas":
                    self.obtener_pcs_conectadas(router, text_widget)
                elif opcion == "ACL":
                    self.obtener_acl(router, text_widget)
                elif opcion == "DHCP":
                    self.obtener_dhcp(router, text_widget)
                elif opcion == "NAT":
                    self.obtener_nat(router, text_widget)
                elif opcion == "DNS":
                    self.obtener_dns(router, text_widget)
                elif opcion == "VPN":
                    self.obtener_vpn(router, text_widget)
                
            except Exception as e:
                text_widget.delete(1.0, tk.END)
                text_widget.insert(tk.END, f"❌ Error obteniendo {opcion}: {str(e)}")
        
        threading.Thread(target=obtener_datos, daemon=True).start()
    
    def obtener_informacion(self, router, text_widget):
        """Obtiene información básica del router"""
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, f"🔧 INFORMACIÓN DEL ROUTER {router.nombre}\n")
        text_widget.insert(tk.END, "═" * 50 + "\n\n")
        
        # Show version
        version = router.ejecutar_comando_show("show version")
        if version:
            text_widget.insert(tk.END, "📊 VERSIÓN DEL SISTEMA:\n")
            text_widget.insert(tk.END, version + "\n\n")
        
        # Show interfaces
        interfaces = router.ejecutar_comando_show("show ip interface brief")
        if interfaces:
            text_widget.insert(tk.END, "🌐 INTERFACES DE RED:\n")
            text_widget.insert(tk.END, interfaces + "\n\n")
        
        # Show running config summary
        hostname = router.ejecutar_comando_show("show running-config | include hostname")
        if hostname:
            text_widget.insert(tk.END, "⚙️ CONFIGURACIÓN BÁSICA:\n")
            text_widget.insert(tk.END, hostname + "\n")
    
    def obtener_enrutamiento(self, router, text_widget):
        """Obtiene información de enrutamiento"""
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, f"🛣️ ENRUTAMIENTO - {router.nombre}\n")
        text_widget.insert(tk.END, "═" * 50 + "\n\n")
        
        # Tabla de rutas
        rutas = router.ejecutar_comando_show("show ip route")
        if rutas:
            text_widget.insert(tk.END, "📋 TABLA DE RUTAS:\n")
            text_widget.insert(tk.END, rutas + "\n\n")
        
        # Protocolos de enrutamiento
        protocolos = router.obtener_protocolos_routing()
        
        if protocolos:
            text_widget.insert(tk.END, "🔄 PROTOCOLOS DE ENRUTAMIENTO:\n")
            for protocolo, info in protocolos.items():
                if info.get('activo'):
                    text_widget.insert(tk.END, f"\n• {protocolo.upper()}:\n")
                    text_widget.insert(tk.END, info.get('info', 'No hay información') + "\n")
                    
                    if 'neighbors' in info:
                        text_widget.insert(tk.END, f"\nVecinos {protocolo.upper()}:\n")
                        text_widget.insert(tk.END, info['neighbors'] + "\n")
        else:
            text_widget.insert(tk.END, "ℹ️ No se detectaron protocolos de enrutamiento dinámico activos.\n")
    
    def obtener_pcs_conectadas(self, router, text_widget):
        """Obtiene información de dispositivos conectados"""
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, f"💻 DISPOSITIVOS CONECTADOS - {router.nombre}\n")
        text_widget.insert(tk.END, "═" * 50 + "\n\n")
        
        # Tabla ARP
        arp = router.ejecutar_comando_show("show arp")
        if arp:
            text_widget.insert(tk.END, "🖥️ TABLA ARP:\n")
            text_widget.insert(tk.END, arp + "\n\n")
        
        # MAC address table
        mac_table = router.ejecutar_comando_show("show mac address-table")
        if mac_table and "Invalid" not in mac_table:
            text_widget.insert(tk.END, "📱 TABLA DE DIRECCIONES MAC:\n")
            text_widget.insert(tk.END, mac_table + "\n\n")
        
        # Interface statistics
        stats = router.ejecutar_comando_show("show interfaces")
        if stats:
            text_widget.insert(tk.END, "📊 ESTADÍSTICAS DE INTERFACES:\n")
            # Mostrar solo un resumen
            lines = stats.split('\n')[:20]  # Primeras 20 líneas
            text_widget.insert(tk.END, '\n'.join(lines) + "\n...\n")
    
    def obtener_acl(self, router, text_widget):
        """Obtiene información de ACLs"""
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, f"🛡️ ACCESS CONTROL LISTS - {router.nombre}\n")
        text_widget.insert(tk.END, "═" * 50 + "\n\n")
        
        # ACLs configuradas
        access_lists = router.ejecutar_comando_show("show access-lists")
        if access_lists and access_lists.strip():
            text_widget.insert(tk.END, "📋 ACLs CONFIGURADAS:\n")
            text_widget.insert(tk.END, access_lists + "\n\n")
        else:
            text_widget.insert(tk.END, "ℹ️ No hay ACLs configuradas.\n\n")
        
        # ACLs aplicadas a interfaces
        running_config = router.ejecutar_comando_show("show running-config | include access-group")
        if running_config and running_config.strip():
            text_widget.insert(tk.END, "🔧 ACLs APLICADAS A INTERFACES:\n")
            text_widget.insert(tk.END, running_config + "\n")
        else:
            text_widget.insert(tk.END, "ℹ️ No hay ACLs aplicadas a interfaces.\n")
    
    def obtener_dhcp(self, router, text_widget):
        """Obtiene información de DHCP"""
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, f"🌐 DHCP CONFIGURATION - {router.nombre}\n")
        text_widget.insert(tk.END, "═" * 50 + "\n\n")
        
        # Configuración DHCP
        dhcp_config = router.ejecutar_comando_show("show running-config | section dhcp")
        if dhcp_config and dhcp_config.strip():
            text_widget.insert(tk.END, "⚙️ CONFIGURACIÓN DHCP:\n")
            text_widget.insert(tk.END, dhcp_config + "\n\n")
        
        # DHCP bindings
        dhcp_bindings = router.ejecutar_comando_show("show ip dhcp binding")
        if dhcp_bindings and dhcp_bindings.strip():
            text_widget.insert(tk.END, "📊 DHCP BINDINGS ACTIVOS:\n")
            text_widget.insert(tk.END, dhcp_bindings + "\n\n")
        else:
            text_widget.insert(tk.END, "ℹ️ No hay DHCP bindings activos.\n\n")
        
        # DHCP statistics
        dhcp_stats = router.ejecutar_comando_show("show ip dhcp server statistics")
        if dhcp_stats and dhcp_stats.strip() and "Invalid" not in dhcp_stats:
            text_widget.insert(tk.END, "📈 ESTADÍSTICAS DHCP:\n")
            text_widget.insert(tk.END, dhcp_stats + "\n")
        else:
            text_widget.insert(tk.END, "ℹ️ No hay estadísticas DHCP disponibles o el servicio no está activo.\n")
    
    def obtener_nat(self, router, text_widget):
        """Obtiene información de NAT"""
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, f"🔄 NETWORK ADDRESS TRANSLATION - {router.nombre}\n")
        text_widget.insert(tk.END, "═" * 50 + "\n\n")
        
        # Configuración NAT
        nat_config = router.ejecutar_comando_show("show running-config | include nat")
        if nat_config and nat_config.strip():
            text_widget.insert(tk.END, "⚙️ CONFIGURACIÓN NAT:\n")
            text_widget.insert(tk.END, nat_config + "\n\n")
        else:
            text_widget.insert(tk.END, "ℹ️ No hay configuración NAT.\n\n")
        
        # Traducciones NAT
        nat_translations = router.ejecutar_comando_show("show ip nat translations")
        if nat_translations and nat_translations.strip():
            text_widget.insert(tk.END, "📊 TRADUCCIONES NAT ACTIVAS:\n")
            text_widget.insert(tk.END, nat_translations + "\n\n")
        else:
            text_widget.insert(tk.END, "ℹ️ No hay traducciones NAT activas.\n\n")
        
        # Estadísticas NAT
        nat_stats = router.ejecutar_comando_show("show ip nat statistics")
        if nat_stats and nat_stats.strip() and "Invalid" not in nat_stats:
            text_widget.insert(tk.END, "📈 ESTADÍSTICAS NAT:\n")
            text_widget.insert(tk.END, nat_stats + "\n")
        else:
            text_widget.insert(tk.END, "ℹ️ No hay estadísticas NAT disponibles.\n")
    
    def obtener_dns(self, router, text_widget):
        """Obtiene información de DNS"""
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, f"🌍 DOMAIN NAME SYSTEM - {router.nombre}\n")
        text_widget.insert(tk.END, "═" * 50 + "\n\n")
        
        # Configuración DNS
        dns_config = router.ejecutar_comando_show("show running-config | include domain")
        if dns_config and dns_config.strip():
            text_widget.insert(tk.END, "⚙️ CONFIGURACIÓN DNS:\n")
            text_widget.insert(tk.END, dns_config + "\n\n")
        
        # Name servers
        name_servers = router.ejecutar_comando_show("show running-config | include name-server")
        if name_servers and name_servers.strip():
            text_widget.insert(tk.END, "🌐 SERVIDORES DNS:\n")
            text_widget.insert(tk.END, name_servers + "\n\n")
        
        # DNS cache (si está disponible)
        dns_cache = router.ejecutar_comando_show("show hosts")
        if dns_cache and dns_cache.strip():
            text_widget.insert(tk.END, "💾 CACHE DNS:\n")
            text_widget.insert(tk.END, dns_cache + "\n")
        else:
            text_widget.insert(tk.END, "ℹ️ No hay información de cache DNS disponible.\n")
    
    def obtener_vpn(self, router, text_widget):
        """Obtiene información de VPN"""
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, f"🔐 VIRTUAL PRIVATE NETWORK - {router.nombre}\n")
        text_widget.insert(tk.END, "═" * 50 + "\n\n")
        
        # IPSec tunnels
        ipsec_sa = router.ejecutar_comando_show("show crypto isakmp sa")
        if ipsec_sa and ipsec_sa.strip() and "Invalid" not in ipsec_sa:
            text_widget.insert(tk.END, "🔑 ISAKMP SECURITY ASSOCIATIONS:\n")
            text_widget.insert(tk.END, ipsec_sa + "\n\n")
        else:
            text_widget.insert(tk.END, "ℹ️ No hay ISAKMP SAs activas.\n\n")
        
        # IPSec SAs
        crypto_sa = router.ejecutar_comando_show("show crypto ipsec sa")
        if crypto_sa and crypto_sa.strip() and "Invalid" not in crypto_sa:
            text_widget.insert(tk.END, "🛡️ IPSEC SECURITY ASSOCIATIONS:\n")
            text_widget.insert(tk.END, crypto_sa + "\n\n")
        else:
            text_widget.insert(tk.END, "ℹ️ No hay IPSec SAs activas.\n\n")
        
        # VPN configuration
        vpn_config = router.ejecutar_comando_show("show running-config | include crypto")
        if vpn_config and vpn_config.strip():
            text_widget.insert(tk.END, "⚙️ CONFIGURACIÓN VPN:\n")
            text_widget.insert(tk.END, vpn_config + "\n")
        else:
            text_widget.insert(tk.END, "ℹ️ No hay configuración VPN detectada.\n")
    
    def actualizar_contenido_existente(self, opcion, router):
        """Actualiza contenido de una pestaña existente"""
        # Esta función se llamaría si la pestaña ya existe
        # Por simplicidad, recreamos el contenido
        pass
    
    def toggle_auto_update(self):
        """Activa/desactiva la actualización automática"""
        if self.auto_update_var.get():
            self.iniciar_auto_update()
        else:
            self.detener_auto_update()
    
    def iniciar_auto_update(self):
        """Inicia la actualización automática"""
        self.actualizar_activo = True
        self.thread_actualizacion = threading.Thread(target=self.auto_update_worker, daemon=True)
        self.thread_actualizacion.start()
    
    def detener_auto_update(self):
        """Detiene la actualización automática"""
        self.actualizar_activo = False
    
    def auto_update_worker(self):
        """Worker para actualización automática"""
        while self.actualizar_activo:
            time.sleep(5)  # Actualizar cada 5 segundos
            if self.actualizar_activo:
                self.root.after(0, self.actualizar_lista_routers)  # Ejecutar en hilo principal
    
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        self.detener_auto_update()
        self.manager.desconectar_todos()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = RouterGUI(root)
    
    # Manejar cierre de ventana
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    root.mainloop()


if __name__ == "__main__":
    main()