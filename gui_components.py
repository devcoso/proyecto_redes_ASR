"""
Módulo con componentes de la interfaz gráfica.
Contiene widgets personalizados y paneles reutilizables.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import Dict, List, Callable, Optional, Tuple
import threading
from datetime import datetime

from topology_config import TopologyConfig, NetworkCommands


class StyledButton(ttk.Button):
    """Botón personalizado con estilos mejorados."""
    
    def __init__(self, parent, text: str, command: Callable, style: str = "default", **kwargs):
        """
        Inicializa un botón estilizado.
        
        Args:
            parent: Widget padre
            text: Texto del botón
            command: Función a ejecutar al hacer clic
            style: Estilo del botón (no usado en ttk)
        """
        super().__init__(parent, text=text, command=command, **kwargs)
        # Los estilos ttk se manejan diferente, por ahora usamos el estilo por defecto


class StatusIndicator(tk.Frame):
    """Indicador de estado visual con color y texto."""
    
    def __init__(self, parent, text: str = "", initial_status: str = "disconnected"):
        """
        Inicializa el indicador de estado.
        
        Args:
            parent: Widget padre
            text: Texto descriptivo
            initial_status: Estado inicial (connected, disconnected, warning)
        """
        super().__init__(parent)
        
        self.status_colors = {
            "connected": TopologyConfig.COLORS["connected"],
            "disconnected": TopologyConfig.COLORS["disconnected"],
            "warning": TopologyConfig.COLORS["warning"]
        }
        
        # Crear indicador circular
        self.indicator = tk.Label(self, text="●", font=("Arial", 16))
        self.indicator.pack(side="left", padx=(0, 5))
        
        # Texto descriptivo
        if text:
            self.text_label = tk.Label(self, text=text)
            self.text_label.pack(side="left")
        
        self.set_status(initial_status)
    
    def set_status(self, status: str):
        """
        Actualiza el estado del indicador.
        
        Args:
            status: Nuevo estado (connected, disconnected, warning)
        """
        color = self.status_colors.get(status, self.status_colors["disconnected"])
        self.indicator.configure(foreground=color)


class NetworkTopologyCanvas(tk.Canvas):
    """Canvas personalizado para dibujar la topología de red."""
    
    def __init__(self, parent, **kwargs):
        """Inicializa el canvas de topología."""
        super().__init__(parent, bg="white", **kwargs)
        self.router_positions = TopologyConfig.get_router_positions()
        self.connections = TopologyConfig.get_connections()
        self.status_colors = {}
        
        # Inicializar estados como desconectado
        for router in self.router_positions:
            self.status_colors[router] = "disconnected"
        
        # Bind eventos del mouse
        self.bind("<Button-1>", self.on_click)
        self.bind("<Motion>", self.on_mouse_motion)
        
        self.draw_topology()
    
    def draw_topology(self):
        """Dibuja la topología completa de la red."""
        self.delete("all")
        
        # Dibujar conexiones primero (para que aparezcan detrás)
        self._draw_connections()
        
        # Dibujar routers
        self._draw_routers()
        
        # Dibujar leyenda
        self._draw_legend()
    
    def _draw_connections(self):
        """Dibuja las conexiones entre routers."""
        for r1, r2 in self.connections:
            if r1 in self.router_positions and r2 in self.router_positions:
                x1, y1 = self.router_positions[r1]
                x2, y2 = self.router_positions[r2]
                
                # Color del enlace basado en el estado de ambos routers
                color = (TopologyConfig.COLORS["connected"] 
                        if (self.status_colors.get(r1) == "connected" and 
                            self.status_colors.get(r2) == "connected")
                        else TopologyConfig.COLORS["disconnected"])
                
                # Línea de conexión
                self.create_line(x1, y1, x2, y2, width=3, fill=color, 
                               tags=("connection", f"conn_{r1}_{r2}"))
                
                # Etiqueta de la conexión (opcional)
                mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
                self.create_text(mid_x, mid_y, text="", font=("Arial", 8), 
                               tags=("connection_label", f"label_{r1}_{r2}"))
    
    def _draw_routers(self):
        """Dibuja los routers en el canvas."""
        for router, (x, y) in self.router_positions.items():
            color = (TopologyConfig.COLORS["connected"] 
                    if self.status_colors.get(router) == "connected"
                    else TopologyConfig.COLORS["disconnected"])
            
            # Círculo principal del router
            self.create_oval(x-25, y-25, x+25, y+25, 
                           fill=color, outline="black", width=2, 
                           tags=("router", f"router_{router}"))
            
            # Círculo interior para efecto visual
            self.create_oval(x-20, y-20, x+20, y+20, 
                           fill="white", outline=color, width=2,
                           tags=("router_inner", f"inner_{router}"))
            
            # Nombre del router
            self.create_text(x, y-40, text=router, 
                           font=("Arial", 12, "bold"), 
                           tags=("router_label", f"name_{router}"))
            
            # IP del router
            router_configs = {r.nombre: r.ip for r in TopologyConfig.ROUTERS_CONFIG}
            ip = router_configs.get(router, "")
            self.create_text(x, y+40, text=ip, 
                           font=("Arial", 9), fill="gray",
                           tags=("router_ip", f"ip_{router}"))
            
            # Estado del router (texto)
            status_text = "●" if self.status_colors.get(router) == "connected" else "●"
            self.create_text(x, y, text=status_text, 
                           font=("Arial", 16), fill="white",
                           tags=("router_status", f"status_{router}"))
    
    def _draw_legend(self):
        """Dibuja la leyenda explicativa."""
        legend_y = 30
        
        # Título de la leyenda
        self.create_text(80, legend_y - 15, text="Estado de la Red:", 
                        font=("Arial", 10, "bold"), anchor="w")
        
        # Conectado
        self.create_oval(20, legend_y, 30, legend_y + 10, 
                        fill=TopologyConfig.COLORS["connected"], outline="black")
        self.create_text(40, legend_y + 5, text="Conectado", 
                        font=("Arial", 9), anchor="w")
        
        # Desconectado
        legend_y += 20
        self.create_oval(20, legend_y, 30, legend_y + 10, 
                        fill=TopologyConfig.COLORS["disconnected"], outline="black")
        self.create_text(40, legend_y + 5, text="Desconectado", 
                        font=("Arial", 9), anchor="w")
    
    def update_router_status(self, router: str, status: str):
        """
        Actualiza el estado visual de un router específico.
        
        Args:
            router: Nombre del router
            status: Nuevo estado (connected, disconnected, warning)
        """
        if router in self.router_positions:
            self.status_colors[router] = status
            self.draw_topology()  # Redibujar para actualizar colores
    
    def update_all_status(self, status_dict: Dict[str, str]):
        """
        Actualiza el estado de todos los routers.
        
        Args:
            status_dict: Diccionario con el estado de cada router
        """
        self.status_colors.update(status_dict)
        self.draw_topology()
    
    def on_click(self, event):
        """Maneja clics en el canvas."""
        # Obtener elemento clickeado
        item = self.find_closest(event.x, event.y)[0]
        tags = self.gettags(item)
        
        # Si se clickeó un router, emitir evento
        for tag in tags:
            if tag.startswith("router_") and not tag.startswith("router_inner"):
                router_name = tag.split("_")[1]
                self.event_generate("<<RouterSelected>>", data=router_name)
                break
    
    def on_mouse_motion(self, event):
        """Maneja movimiento del mouse para tooltips."""
        item = self.find_closest(event.x, event.y)[0]
        tags = self.gettags(item)
        
        # Mostrar información del router en hover (implementar si es necesario)
        pass


class LogPanel(tk.Frame):
    """Panel de logs con filtrado y búsqueda."""
    
    def __init__(self, parent):
        """Inicializa el panel de logs."""
        super().__init__(parent)
        
        # Frame superior con controles
        control_frame = tk.Frame(self)
        control_frame.pack(fill="x", padx=5, pady=5)
        
        # Botón limpiar
        ttk.Button(control_frame, text="Limpiar", 
                  command=self.clear_logs).pack(side="left", padx=(0, 5))
        
        # Botón exportar
        ttk.Button(control_frame, text="Exportar", 
                  command=self.export_logs).pack(side="left", padx=(0, 5))
        
        # Campo de búsqueda
        tk.Label(control_frame, text="Filtrar:").pack(side="left", padx=(10, 5))
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(control_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side="left", padx=(0, 5))
        search_entry.bind("<KeyRelease>", self.filter_logs)
        
        # Área de texto principal
        self.text_area = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, height=15,
            font=("Consolas", 9)
        )
        self.text_area.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configurar tags para colores
        self.configure_text_tags()
        
        self.all_logs = []  # Almacenar todos los logs para filtrado
    
    def configure_text_tags(self):
        """Configura los tags de color para diferentes tipos de mensajes."""
        self.text_area.tag_configure("info", foreground="blue")
        self.text_area.tag_configure("success", foreground="green")
        self.text_area.tag_configure("warning", foreground="orange")
        self.text_area.tag_configure("error", foreground="red")
        self.text_area.tag_configure("timestamp", foreground="gray")
    
    def add_log(self, message: str, log_type: str = "info", router: str = ""):
        """
        Añade un mensaje al log.
        
        Args:
            message: Mensaje a añadir
            log_type: Tipo de log (info, success, warning, error)
            router: Router relacionado (opcional)
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        router_prefix = f"[{router}] " if router else ""
        full_message = f"[{timestamp}] {router_prefix}{message}\n"
        
        # Almacenar en la lista completa
        self.all_logs.append({
            'timestamp': timestamp,
            'router': router,
            'message': message,
            'type': log_type,
            'full': full_message
        })
        
        # Mostrar en el área de texto
        self.text_area.insert(tk.END, f"[{timestamp}] ", "timestamp")
        if router:
            self.text_area.insert(tk.END, f"[{router}] ", "info")
        self.text_area.insert(tk.END, f"{message}\n", log_type)
        
        # Auto-scroll
        self.text_area.see(tk.END)
        
        # Limitar número de líneas (mantener últimas 1000)
        if len(self.all_logs) > 1000:
            self.all_logs = self.all_logs[-1000:]
            self.refresh_display()
    
    def clear_logs(self):
        """Limpia todos los logs."""
        self.text_area.delete(1.0, tk.END)
        self.all_logs.clear()
    
    def filter_logs(self, event=None):
        """Filtra los logs basado en el texto de búsqueda."""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            self.refresh_display()
            return
        
        # Limpiar y mostrar solo logs filtrados
        self.text_area.delete(1.0, tk.END)
        
        for log_entry in self.all_logs:
            if (search_term in log_entry['message'].lower() or 
                search_term in log_entry['router'].lower()):
                
                self.text_area.insert(tk.END, f"[{log_entry['timestamp']}] ", "timestamp")
                if log_entry['router']:
                    self.text_area.insert(tk.END, f"[{log_entry['router']}] ", "info")
                self.text_area.insert(tk.END, f"{log_entry['message']}\n", log_entry['type'])
        
        self.text_area.see(tk.END)
    
    def refresh_display(self):
        """Refresca la visualización completa de logs."""
        self.text_area.delete(1.0, tk.END)
        
        for log_entry in self.all_logs:
            self.text_area.insert(tk.END, f"[{log_entry['timestamp']}] ", "timestamp")
            if log_entry['router']:
                self.text_area.insert(tk.END, f"[{log_entry['router']}] ", "info")
            self.text_area.insert(tk.END, f"{log_entry['message']}\n", log_entry['type'])
        
        self.text_area.see(tk.END)
    
    def export_logs(self):
        """Exporta los logs a un archivo."""
        from tkinter import filedialog
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    for log_entry in self.all_logs:
                        f.write(log_entry['full'])
                
                self.add_log(f"Logs exportados a {filename}", "success")
            except Exception as e:
                self.add_log(f"Error exportando logs: {e}", "error")


class ConfigurationDialog(tk.Toplevel):
    """Diálogo personalizado para configuraciones."""
    
    def __init__(self, parent, config_type: str, router_name: str, callback: Callable):
        """
        Inicializa el diálogo de configuración.
        
        Args:
            parent: Ventana padre
            config_type: Tipo de configuración
            router_name: Nombre del router
            callback: Función a llamar con los comandos
        """
        super().__init__(parent)
        
        self.config_type = config_type
        self.router_name = router_name
        self.callback = callback
        
        self.setup_dialog()
        self.load_template()
    
    def setup_dialog(self):
        """Configura la estructura del diálogo."""
        self.title(f"Configurar {self.config_type} - {self.router_name}")
        self.geometry("700x500")
        self.transient(self.master)
        self.grab_set()
        
        # Centrar el diálogo
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        
        # Frame principal
        main_frame = ttk.Frame(self, padding="15")
        main_frame.pack(fill="both", expand=True)
        
        # Título y descripción
        title_label = ttk.Label(
            main_frame, 
            text=f"Configuración de {self.config_type}",
            font=("Arial", 14, "bold")
        )
        title_label.pack(anchor="w", pady=(0, 10))
        
        desc_label = ttk.Label(
            main_frame, 
            text=f"Router de destino: {self.router_name}",
            font=("Arial", 10)
        )
        desc_label.pack(anchor="w", pady=(0, 15))
        
        # Frame para botones de plantilla
        template_frame = ttk.LabelFrame(main_frame, text="Plantillas", padding="10")
        template_frame.pack(fill="x", pady=(0, 15))
        
        # Botones de plantillas comunes
        templates = ["Básico", "Avanzado", "Personalizado"]
        for template in templates:
            ttk.Button(
                template_frame, 
                text=template,
                command=lambda t=template: self.load_template(t)
            ).pack(side="left", padx=(0, 10))
        
        # Área de texto para comandos
        commands_label = ttk.Label(main_frame, text="Comandos de configuración:")
        commands_label.pack(anchor="w", pady=(0, 5))
        
        self.commands_text = scrolledtext.ScrolledText(
            main_frame, 
            height=15, 
            wrap=tk.WORD,
            font=("Consolas", 10)
        )
        self.commands_text.pack(fill="both", expand=True, pady=(0, 15))
        
        # Frame de botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x")
        
        # Botones de acción
        ttk.Button(
            button_frame, 
            text="Validar Sintaxis",
            command=self.validate_syntax
        ).pack(side="left")
        
        ttk.Button(
            button_frame, 
            text="Vista Previa",
            command=self.preview_config
        ).pack(side="left", padx=(10, 0))
        
        # Botones principales
        ttk.Button(
            button_frame, 
            text="Aplicar",
            command=self.apply_config
        ).pack(side="right")
        
        ttk.Button(
            button_frame, 
            text="Cancelar",
            command=self.destroy
        ).pack(side="right", padx=(0, 10))
    
    def load_template(self, template_type: str = "Básico"):
        """Carga una plantilla de configuración."""
        template = TopologyConfig.get_config_template(self.config_type)
        
        # Limpiar área de texto
        self.commands_text.delete("1.0", tk.END)
        
        # Insertar comandos de la plantilla
        commands = template.get("comandos", [])
        self.commands_text.insert("1.0", "\n".join(commands))
    
    def validate_syntax(self):
        """Valida la sintaxis básica de los comandos."""
        commands = self.get_commands()
        
        if not commands:
            messagebox.showwarning("Advertencia", "No hay comandos para validar")
            return
        
        # Validación básica
        errors = []
        for i, cmd in enumerate(commands, 1):
            if not cmd.strip():
                continue
            
            # Verificar comandos que requieren modo de configuración
            config_commands = ["interface", "router", "vlan", "access-list", "ip"]
            if any(cmd.strip().startswith(cc) for cc in config_commands):
                if not cmd.strip().startswith("!"):  # No es comentario
                    continue  # Comando válido
            
            # Verificar sintaxis básica
            if cmd.strip() and not cmd.strip().startswith("!"):
                if len(cmd.strip()) < 3:
                    errors.append(f"Línea {i}: Comando muy corto")
        
        if errors:
            messagebox.showwarning("Errores de Sintaxis", "\n".join(errors))
        else:
            messagebox.showinfo("Validación", "Sintaxis válida")
    
    def preview_config(self):
        """Muestra una vista previa de la configuración."""
        commands = self.get_commands()
        
        if not commands:
            messagebox.showwarning("Advertencia", "No hay comandos para previsualizar")
            return
        
        preview_window = tk.Toplevel(self)
        preview_window.title("Vista Previa de Configuración")
        preview_window.geometry("600x400")
        preview_window.transient(self)
        
        # Área de texto de solo lectura
        preview_text = scrolledtext.ScrolledText(
            preview_window, 
            wrap=tk.WORD,
            font=("Consolas", 10),
            state="disabled"
        )
        preview_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Insertar contenido
        preview_text.config(state="normal")
        preview_text.insert("1.0", f"Configuración para {self.router_name}\n")
        preview_text.insert(tk.END, "=" * 50 + "\n\n")
        
        for i, cmd in enumerate(commands, 1):
            preview_text.insert(tk.END, f"{i:2d}: {cmd}\n")
        
        preview_text.config(state="disabled")
    
    def get_commands(self) -> List[str]:
        """Obtiene la lista de comandos del área de texto."""
        content = self.commands_text.get("1.0", tk.END).strip()
        commands = [cmd.strip() for cmd in content.split("\n") if cmd.strip()]
        return commands
    
    def apply_config(self):
        """Aplica la configuración."""
        commands = self.get_commands()
        
        if not commands:
            messagebox.showwarning("Advertencia", "Ingrese al menos un comando")
            return
        
        # Confirmar aplicación
        result = messagebox.askyesno(
            "Confirmar Configuración",
            f"¿Está seguro de aplicar esta configuración a {self.router_name}?\n\n"
            f"Se ejecutarán {len(commands)} comandos."
        )
        
        if result:
            self.callback(commands)
            self.destroy()


class ProgressDialog(tk.Toplevel):
    """Diálogo de progreso para operaciones largas."""
    
    def __init__(self, parent, title: str = "Procesando..."):
        """
        Inicializa el diálogo de progreso.
        
        Args:
            parent: Ventana padre
            title: Título del diálogo
        """
        super().__init__(parent)
        
        self.title(title)
        self.geometry("400x150")
        self.transient(parent)
        self.grab_set()
        
        # Centrar diálogo
        self.update_idletasks()
        x = (self.winfo_screenwidth() - self.winfo_width()) // 2
        y = (self.winfo_screenheight() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")
        
        # Frame principal
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Etiqueta de estado
        self.status_label = ttk.Label(
            main_frame, 
            text="Iniciando...",
            font=("Arial", 10)
        )
        self.status_label.pack(pady=(0, 15))
        
        # Barra de progreso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            length=300
        )
        self.progress_bar.pack(pady=(0, 15))
        
        # Botón cancelar
        self.cancel_button = ttk.Button(
            main_frame,
            text="Cancelar",
            command=self.cancel_operation
        )
        self.cancel_button.pack()
        
        self.cancelled = False
    
    def update_progress(self, value: float, status: str = ""):
        """
        Actualiza el progreso.
        
        Args:
            value: Valor de progreso (0-100)
            status: Texto de estado opcional
        """
        self.progress_var.set(value)
        if status:
            self.status_label.config(text=status)
        self.update()
    
    def set_indeterminate(self):
        """Configura la barra como indeterminada."""
        self.progress_bar.config(mode="indeterminate")
        self.progress_bar.start()
    
    def cancel_operation(self):
        """Marca la operación como cancelada."""
        self.cancelled = True
        self.destroy()
    
    def is_cancelled(self) -> bool:
        """Verifica si la operación fue cancelada."""
        return self.cancelled