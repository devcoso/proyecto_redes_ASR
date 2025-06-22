"""
Interfaz gráfica principal para gestión de topología de red.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time
from datetime import datetime

# Importar módulos locales
from network_connection import RouterManager
import topology_config as config


class NetworkTopologyGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Topología de Red GNS3")
        self.root.geometry("1200x800")
        
        # Configurar estilos
        self.setup_styles()
        
        # Inicializar el manager de routers
        self.router_manager = RouterManager()
        self.selected_router = None 
        self.monitoring_active = False
        self.status_colors = {}
        
        # Configurar routers predefinidos
        self.setup_predefined_routers()
        
        # Crear la interfaz
        self.create_interface()
        
        # Iniciar monitoreo automático
        self.start_monitoring()
    
    def setup_styles(self):
        """Configura los estilos TTK"""
        style = ttk.Style()
        
        # Configurar estilos personalizados
        style.configure('Success.TButton', foreground='white')
        style.configure('Danger.TButton', foreground='white')
        style.configure('Title.TLabel', font=('Arial', 12, 'bold'))
        
        # Mapear estilos si el tema lo soporta
        try:
            style.map('Success.TButton', background=[('active', '#45a049'), ('!active', '#4CAF50')])
            style.map('Danger.TButton', background=[('active', '#da190b'), ('!active', '#f44336')])
        except:
            pass  # Si el tema no soporta colores personalizados
    
    def setup_predefined_routers(self):
        """Configura los routers predefinidos"""
        for nombre, ip, usuario, password in config.ROUTERS_CONFIG:
            self.router_manager.agregar_router(nombre, ip, usuario, password)
            self.status_colors[nombre] = "red"  # Inicialmente desconectado
    
    def create_interface(self):
        """Crea la interfaz gráfica principal"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Panel de control izquierdo
        self.create_control_panel(main_frame)
        
        # Panel central con topología y resultados
        self.create_center_panel(main_frame)
        
        # Panel de estado inferior
        self.create_status_panel(main_frame)
    
    def create_control_panel(self, parent):
        """Crea el panel de control izquierdo"""
        control_frame = ttk.LabelFrame(parent, text="Panel de Control", padding="10")
        control_frame.grid(row=0, column=0, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Botones de conexión
        connection_frame = ttk.LabelFrame(control_frame, text="Conexiones", padding="5")
        connection_frame.pack(fill="x", pady=(0, 10))
        
        ttk.Button(connection_frame, text="Conectar Todos", style='Success.TButton',
                  command=self.connect_all_routers).pack(fill="x", pady=2)
        ttk.Button(connection_frame, text="Desconectar Todos", style='Danger.TButton',
                  command=self.disconnect_all_routers).pack(fill="x", pady=2)
        
        # Selección de router
        router_frame = ttk.LabelFrame(control_frame, text="Seleccionar Router", padding="5")
        router_frame.pack(fill="x", pady=(0, 10))
        
        self.router_var = tk.StringVar(value="R1")
        router_combo = ttk.Combobox(router_frame, textvariable=self.router_var, 
                                   values=["R1", "R2", "R3", "R4", "R5"], state="readonly")
        router_combo.pack(fill="x", pady=2)
        router_combo.bind("<<ComboboxSelected>>", self.on_router_selected)
        
        # Botones de consulta
        query_frame = ttk.LabelFrame(control_frame, text="Consultas", padding="5")
        query_frame.pack(fill="x", pady=(0, 10))
        
        for text, command in config.QUERY_COMMANDS.items():
            ttk.Button(query_frame, text=text, 
                      command=lambda cmd=command, desc=text: self.execute_query(cmd, desc)
                      ).pack(fill="x", pady=1)
        
        # Botones de configuración
        config_frame = ttk.LabelFrame(control_frame, text="Configuraciones", padding="5")
        config_frame.pack(fill="x", pady=(0, 10))
        
        config_buttons = [
            ("Configurar ACL", "ACL"),
            ("Configurar DHCP", "DHCP"),
            ("Configurar NAT", "NAT"),
            ("Configurar VLAN", "VLAN"),
            ("Configurar SNMP", "SNMP"),
            ("Configurar QoS", "QoS"),
            ("Configurar Enrutamiento", "Enrutamiento")
        ]
        
        for text, config_type in config_buttons:
            ttk.Button(config_frame, text=text, 
                      command=lambda ct=config_type: self.config_dialog(ct)
                      ).pack(fill="x", pady=1)
    
    def create_center_panel(self, parent):
        """Crea el panel central con topología y resultados"""
        center_frame = ttk.Frame(parent)
        center_frame.grid(row=0, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        center_frame.columnconfigure(0, weight=1)
        center_frame.rowconfigure(0, weight=1)
        center_frame.rowconfigure(1, weight=1)
        
        # Canvas para la topología
        topology_frame = ttk.LabelFrame(center_frame, text="Topología de Red", padding="5")
        topology_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 5))
        topology_frame.columnconfigure(0, weight=1)
        topology_frame.rowconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(topology_frame, bg="white", height=300)
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Dibujar topología
        self.draw_topology()
        
        # Panel de resultados
        results_frame = ttk.LabelFrame(center_frame, text="Consola", padding="5")
        results_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(1, weight=1)
        
        # Frame para botones de resultados
        results_buttons_frame = ttk.Frame(results_frame)
        results_buttons_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Button(results_buttons_frame, text="Limpiar", 
                  command=self.clear_results).pack(side="left", padx=(0, 5))
        ttk.Button(results_buttons_frame, text="Exportar", 
                  command=self.export_results).pack(side="left")
        
        self.results_text = scrolledtext.ScrolledText(results_frame, wrap=tk.WORD, height=15)
        self.results_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar tags para colores
        self.setup_text_tags()
    
    def create_status_panel(self, parent):
        """Crea el panel de estado inferior"""
        status_frame = ttk.LabelFrame(parent, text="Estado del Sistema", padding="5")
        status_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, text="Sistema iniciado - Listo para conectar")
        self.status_label.pack(side=tk.LEFT)
        
        # Indicador de monitoreo
        self.monitoring_label = ttk.Label(status_frame, text="● Monitoreo activo", foreground="green")
        self.monitoring_label.pack(side=tk.RIGHT)
    
    def setup_text_tags(self):
        """Configura tags de color para el área de resultados"""
        self.results_text.tag_configure("success", foreground="green", font=("Consolas", 9, "bold"))
        self.results_text.tag_configure("error", foreground="red", font=("Consolas", 9, "bold"))
        self.results_text.tag_configure("warning", foreground="orange", font=("Consolas", 9, "bold"))
        self.results_text.tag_configure("info", foreground="blue", font=("Consolas", 9, "bold"))
        self.results_text.tag_configure("timestamp", foreground="gray", font=("Consolas", 8))
    
    def draw_topology(self):
        """Dibuja la topología de red en el canvas"""
        self.canvas.delete("all")
        
        # Dibujar conexiones
        for r1, r2 in config.CONNECTIONS:
            x1, y1 = config.ROUTER_POSITIONS[r1]
            x2, y2 = config.ROUTER_POSITIONS[r2]
            
            # Determinar color del enlace basado en el estado de ambos routers
            color = "green" if (self.status_colors.get(r1) == "green" and 
                              self.status_colors.get(r2) == "green") else "red"
            
            self.canvas.create_line(x1, y1, x2, y2, width=2, fill=color, tags="connection")
        
        # Dibujar routers
        for router, (x, y) in config.ROUTER_POSITIONS.items():
            color = self.status_colors.get(router, "red")
            
            # Círculo del router
            self.canvas.create_oval(x-20, y-20, x+20, y+20, 
                                   fill=color, outline="black", width=2, tags="router")
            
            # Etiqueta del router
            self.canvas.create_text(x, y-35, text=router, font=("Arial", 10, "bold"), tags="label")
            
            # IP del router
            router_obj = self.router_manager.obtener_router(router)
            if router_obj:
                self.canvas.create_text(x, y+35, text=router_obj.ip, 
                                      font=("Arial", 8), tags="ip")
    
    def connect_all_routers(self):
        """Conecta a todos los routers"""
        def connect_thread():
            self.update_status("Conectando a todos los routers...")
            self.add_result(f"\n[{datetime.now().strftime('%H:%M:%S')}] Iniciando conexiones...\n", "timestamp")
            
            results = self.router_manager.conectar_todos()
            
            for nombre, resultado in results.items():
                if resultado:
                    self.status_colors[nombre] = "green"
                    self.add_result(f"✓ {nombre} conectado exitosamente\n", "success")
                else:
                    self.status_colors[nombre] = "red"
                    self.add_result(f"✗ Error conectando a {nombre}\n", "error")
            
            self.root.after(0, self.draw_topology)
            self.update_status("Conexiones completadas")
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def disconnect_all_routers(self):
        """Desconecta todos los routers"""
        self.router_manager.desconectar_todos()
        for nombre in self.status_colors:
            self.status_colors[nombre] = "red"
        
        self.draw_topology()
        self.update_status("Todos los routers desconectados")
        self.add_result(f"\n[{datetime.now().strftime('%H:%M:%S')}] Todos los routers desconectados\n", "timestamp")
    
    def on_router_selected(self, event=None):
        """Maneja la selección de router"""
        self.selected_router = self.router_var.get()
        self.update_status(f"Router seleccionado: {self.selected_router}")
    
    def execute_query(self, command, description):
        """Ejecuta una consulta en el router seleccionado"""
        if not self.selected_router:
            messagebox.showwarning("Advertencia", "Seleccione un router primero")
            return
        
        def query_thread():
            router = self.router_manager.obtener_router(self.selected_router)
            if not router:
                self.root.after(0, lambda: messagebox.showerror("Error", "Router no encontrado"))
                return
            
            self.update_status(f"Ejecutando {description} en {self.selected_router}...")
            
            result = router.obtener_informacion(command)
            
            timestamp = datetime.now().strftime('%H:%M:%S')
            self.add_result(f"\n[{timestamp}] {description} - {self.selected_router}\n", "timestamp")
            self.add_result("=" * 60 + "\n", "info")
            
            if result:
                self.add_result(result + "\n", "success")
            else:
                if result.strip():
                    self.add_result(result + "\n", "success")
                else:
                    self.add_result("No se obtuvo información (vacío)\n", "info")
            
            self.add_result("=" * 60 + "\n", "info")
            self.update_status("Consulta completada")
        
        threading.Thread(target=query_thread, daemon=True).start()
    
    def config_dialog(self, config_type):
        """Muestra diálogo para configuración"""
        if not self.selected_router:
            messagebox.showwarning("Advertencia", "Seleccione un router primero")
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Configurar {config_type} - {self.selected_router}")
        dialog.geometry("1200x800")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Frame principal
        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill="both", expand=True)
        
        # Instrucciones
        ttk.Label(main_frame, text=f"Comandos de configuración para {config_type}:", 
                 style='Title.TLabel').pack(anchor="w")
        
        # Área de texto para comandos
        commands_text = scrolledtext.ScrolledText(main_frame, height=15, wrap=tk.WORD)
        commands_text.pack(fill="both", expand=True, pady=(5, 10))
        
        # Insertar comandos por defecto
        default_commands = config.CONFIG_TEMPLATES.get(config_type, [])
        commands_text.insert("1.0", "\n".join(default_commands))
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        def apply_config():
            commands = commands_text.get("1.0", tk.END).strip().split("\n")
            commands = [cmd.strip() for cmd in commands if cmd.strip()]
            
            if not commands:
                messagebox.showwarning("Advertencia", "Ingrese al menos un comando")
                return
            
            def config_thread():
                router = self.router_manager.obtener_router(self.selected_router)
                if router:
                    result = router.configurar(commands)
                    
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    self.add_result(f"\n[{timestamp}] Configuración {config_type} - {self.selected_router}\n", "timestamp")
                    self.add_result("=" * 60 + "\n", "info")
                    
                    if result:
                        self.add_result("✓ Configuración aplicada exitosamente\n", "success")
                        self.add_result(f"Comandos ejecutados:\n", "info")
                        for cmd in commands:
                            self.add_result(f"  - {cmd}\n", "info")
                    else:
                        self.add_result("✗ Error aplicando configuración\n", "error")
                    
                    self.add_result("=" * 60 + "\n", "info")
                    
                    self.root.after(0, dialog.destroy)
            
            threading.Thread(target=config_thread, daemon=True).start()
        
        ttk.Button(button_frame, text="Aplicar", command=apply_config).pack(side="right", padx=(5, 0))
        ttk.Button(button_frame, text="Cancelar", command=dialog.destroy).pack(side="right")
    
    def start_monitoring(self):
        """Inicia el monitoreo automático de routers"""
        self.monitoring_active = True
        
        def monitor_thread():
            while self.monitoring_active:
                try:
                    for nombre, router in self.router_manager.routers.items():
                        if router.conectado:
                            if router.verificar_conexion():
                                self.status_colors[nombre] = "green"
                            else:
                                self.status_colors[nombre] = "red"
                        else:
                            self.status_colors[nombre] = "red"
                    
                    # Actualizar topología en el hilo principal
                    self.root.after(0, self.draw_topology)
                    
                    time.sleep(10)  # Monitorear cada 10 segundos
                except Exception as e:
                    print(f"Error en monitoreo: {e}")
                    time.sleep(10)
        
        threading.Thread(target=monitor_thread, daemon=True).start()
    
    def update_status(self, message):
        """Actualiza el mensaje de estado"""
        def update():
            self.status_label.config(text=message)
        
        self.root.after(0, update)
    
    def add_result(self, text, tag=""):
        """Añade texto al área de resultados"""
        def add():
            self.results_text.insert(tk.END, text, tag)
            self.results_text.see(tk.END)
        
        self.root.after(0, add)
    
    def clear_results(self):
        """Limpia el área de resultados"""
        self.results_text.delete(1.0, tk.END)
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.add_result(f"[{timestamp}] Se ha limpiado la consola\n", "info")
    
    def export_results(self):
        """Exporta los resultados a un archivo"""
        from tkinter import filedialog
        
        content = self.results_text.get(1.0, tk.END)
        if not content.strip():
            messagebox.showinfo("Información", "No hay información para exportar")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")],
            title="Exportar"
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(f"Consola exportada - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(content)
                
                self.add_result(f"Consola exportada a: {filename}\n", "success")
                messagebox.showinfo("Éxito", f"Consola exportada a:\n{filename}")
                
            except Exception as e:
                self.add_result(f"Error exportando: {e}\n", "error")
                messagebox.showerror("Error", f"Error exportando archivo:\n{e}")
    
    def on_closing(self):
        """Maneja el cierre de la aplicación"""
        self.monitoring_active = False
        self.router_manager.desconectar_todos()
        self.root.destroy()


def main():
    """Función principal"""
    root = tk.Tk()
    app = NetworkTopologyGUI(root)
    
    # Configurar el cierre de la aplicación
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    
    # Centrar la ventana
    root.update_idletasks()
    x = (root.winfo_screenwidth() - root.winfo_width()) // 2
    y = (root.winfo_screenheight() - root.winfo_height()) // 2
    root.geometry(f"+{x}+{y}")
    
    # Iniciar la aplicación
    root.mainloop()


if __name__ == "__main__":
    main()