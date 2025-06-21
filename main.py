from netmiko import ConnectHandler

def conectar_cisco_antiguo(ip, usuario, password):
    device = {
        'device_type': 'cisco_ios',
        'host': ip,
        'username': usuario,
        'password': password,
        'port': 22,
        # Configuraciones para protocolos antiguos
        'ssh_config_file': None,  # No usar archivo de config SSH
        'allow_agent': False,
        'disabled_algorithms': {
            'kex': [],  # No deshabilitar intercambio de claves
            'server_host_key_algs': [],
            'encrypt': [],
            'mac': []
        },
        # Parámetros específicos para equipos antiguos
        'conn_timeout': 20,
        'auth_timeout': 20,
        'banner_timeout': 15,
    }
    
    try:
        connection = ConnectHandler(**device)
        return connection
    except Exception as e:
        print(f"Error detallado: {e}")
        return None
    
def main():
    ip = input("Ingrese la dirección IP del dispositivo: ")
    usuario = input("Ingrese el nombre de usuario: ")
    password = input("Ingrese la contraseña: ")
    
    conexion = conectar_cisco_antiguo(ip, usuario, password)
    
    if conexion:
        print("Conexión exitosa al dispositivo Cisco antiguo.")
        # Aquí puedes agregar más lógica para interactuar con el dispositivo
        try:
            # Ejecutar un comando de prueba
            output = conexion.send_command("show version")
            print(output)
        except Exception as e:
            print(f"Error al ejecutar el comando: {e}")
        finally:
            conexion.disconnect()
    else:
        print("No se pudo conectar al dispositivo.")

if __name__ == "__main__":
    main()