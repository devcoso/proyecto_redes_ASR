import sys
import os

# Verificar versión de Python
if sys.version_info < (3, 6):
    print("Error: Se requiere Python 3.6 o superior")
    sys.exit(1)

def check_dependencies():
    """Verifica que las dependencias estén instaladas"""
    required_modules = ['netmiko', 'tkinter']
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing_modules.append(module)
    
    if missing_modules:
        print(f"Error: Módulos faltantes: {', '.join(missing_modules)}")
        return False
    
    print("Todas las dependencias están disponibles")
    return True

def main():
    """Función principal"""
    print("Gestor de Topología de Red GNS3")
    print("=" * 40)
    
    # Verificar dependencias
    if not check_dependencies():
        input("\nPresione Enter para salir...")
        return
    
    try:
        # Importar y ejecutar la aplicación
        from network_gui import main as run_gui
        run_gui()
        
    except ImportError as e:
        print(f"Error de importación: {e}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()