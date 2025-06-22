"""
Módulo para manejar conexiones SSH a routers Cisco.
"""

from netmiko import ConnectHandler
import time
import threading
from datetime import datetime


class SSHRouterConnection:
    """
    Clase para manejar conexiones SSH persistentes a routers Cisco.
    Mantiene la conexión viva y proporciona métodos para obtener y configurar información.
    """
    
    def __init__(self, ip, usuario, password, nombre="Router"):
        self.ip = ip
        self.usuario = usuario
        self.password = password
        self.nombre = nombre
        self.conexion = None
        self.conectado = False
        self.ultimo_comando = None
        self.keepalive_interval = 30  # segundos
        self.keepalive_thread = None
        self.keepalive_activo = False
        
        # Configuración del dispositivo
        self.device_config = {
            'device_type': 'cisco_ios',
            'host': self.ip,
            'username': self.usuario,
            'password': self.password,
            'port': 22,
            'ssh_config_file': None,
            'allow_agent': False,
            'disabled_algorithms': {
                'kex': [],
                'server_host_key_algs': [],
                'encrypt': [],
                'mac': []
            },
            'conn_timeout': 20,
            'auth_timeout': 20,
            'banner_timeout': 15,
        }
    
    def conectar(self):
        """Establece la conexión SSH al router"""
        try:
            print(f"Conectando a {self.nombre} ({self.ip})...")
            self.conexion = ConnectHandler(**self.device_config)
            self.conectado = True
            print(f"✓ Conexión exitosa a {self.nombre}")
            
            # Iniciar keepalive
            self._iniciar_keepalive()
            return True
            
        except Exception as e:
            print(f"✗ Error conectando a {self.nombre}: {e}")
            self.conectado = False
            return False
    
    def desconectar(self):
        """Cierra la conexión SSH"""
        try:
            self._detener_keepalive()
            if self.conexion and self.conectado:
                self.conexion.disconnect()
                print(f"✓ Desconectado de {self.nombre}")
            self.conectado = False
        except Exception as e:
            print(f"Error al desconectar de {self.nombre}: {e}")
    
    def verificar_conexion(self):
        """Verifica si la conexión está activa"""
        if not self.conexion or not self.conectado:
            return False
        
        try:
            # Enviar comando simple para verificar conectividad
            self.conexion.send_command("show clock", expect_string=r"#")
            return True
        except:
            self.conectado = False
            return False
    
    def reconectar(self):
        """Intenta reconectar al router"""
        print(f"Intentando reconectar a {self.nombre}...")
        self.desconectar()
        time.sleep(2)
        return self.conectar()
    
    def obtener_informacion(self, comando):
        """
        Ejecuta comandos de consulta (show commands)
        """
        if not self._verificar_y_reconectar():
            return None
        
        try:
            print(f"[{self.nombre}] Ejecutando: {comando}")
            resultado = self.conexion.send_command(comando)
            self.ultimo_comando = datetime.now()
            return resultado
        except Exception as e:
            print(f"Error ejecutando '{comando}' en {self.nombre}: {e}")
            return None
    
    def configurar(self, comandos):
        """
        Ejecuta comandos de configuración
        comandos: lista de comandos o string único
        """
        if not self._verificar_y_reconectar():
            return False
        
        try:
            if isinstance(comandos, str):
                comandos = [comandos]
            
            print(f"[{self.nombre}] Ejecutando {len(comandos)} comando(s) de configuración")
            resultado = self.conexion.send_config_set(comandos)
            self.ultimo_comando = datetime.now()
            print(f"✓ Configuración aplicada en {self.nombre}")
            return resultado
        except Exception as e:
            print(f"✗ Error en configuración de {self.nombre}: {e}")
            return False
    
    def _verificar_y_reconectar(self):
        """Verifica conexión y reconecta si es necesario"""
        if not self.verificar_conexion():
            return self.reconectar()
        return True
    
    def _iniciar_keepalive(self):
        """Inicia el hilo de keepalive para mantener la conexión viva"""
        self.keepalive_activo = True
        self.keepalive_thread = threading.Thread(target=self._keepalive_worker, daemon=True)
        self.keepalive_thread.start()
    
    def _detener_keepalive(self):
        """Detiene el keepalive"""
        self.keepalive_activo = False
        if self.keepalive_thread:
            self.keepalive_thread.join(timeout=2)
    
    def _keepalive_worker(self):
        """Worker que mantiene la conexión viva"""
        while self.keepalive_activo and self.conectado:
            try:
                time.sleep(self.keepalive_interval)
                if self.keepalive_activo:
                    self.conexion.send_command("show clock", expect_string=r"#")
            except:
                if self.keepalive_activo:
                    print(f"Keepalive falló para {self.nombre}, intentando reconectar...")
                    self.reconectar()
    
    def __str__(self):
        estado = "Conectado" if self.conectado else "Desconectado"
        return f"{self.nombre} ({self.ip}) - {estado}"


class RouterManager:
    """
    Clase para manejar múltiples conexiones de routers
    """
    
    def __init__(self):
        self.routers = {}
    
    def agregar_router(self, nombre, ip, usuario, password):
        """Agrega un router al manager"""
        router = SSHRouterConnection(ip, usuario, password, nombre)
        self.routers[nombre] = router
        return router
    
    def conectar_todos(self):
        """Conecta a todos los routers"""
        resultados = {}
        for nombre, router in self.routers.items():
            resultados[nombre] = router.conectar()
        return resultados
    
    def desconectar_todos(self):
        """Desconecta todos los routers"""
        for router in self.routers.values():
            router.desconectar()
    
    def obtener_router(self, nombre):
        """Obtiene un router específico"""
        return self.routers.get(nombre)
    
    def listar_routers(self):
        """Lista todos los routers y su estado"""
        for router in self.routers.values():
            print(router)