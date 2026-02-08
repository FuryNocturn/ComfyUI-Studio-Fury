import os
import shutil
import importlib
import importlib.util
import traceback
import folder_paths
import filecmp
import sys
import inspect

from server import PromptServer
from aiohttp import web

# ==============================================================================
#  CONFIGURACIÓN
# ==============================================================================
EXTENSION_NAME = "StudioFury"
DEBUG_MODE = True

# Archivos a ignorar para que no intente cargarlos como nodos
IGNORE_FILES = {"__init__.py", "sf_io.py", "setup.py", "install.py"}

# ==============================================================================
#  HELPERS
# ==============================================================================
# Inyectar el root al path para que funcionen los imports relativos y absolutos
node_root = os.path.dirname(os.path.abspath(__file__))
if node_root not in sys.path:
    sys.path.append(node_root)

# ==============================================================================
#  1. API KILL SWITCH
# ==============================================================================
try:
    routes = PromptServer.instance.routes

    @routes.post('/studiofury/system/shutdown')
    async def fury_shutdown(request):
        print(f"\n🛑 [{EXTENSION_NAME}] Apagando servidor...")
        sys.stdout.flush()
        os._exit(0)

    @routes.post('/studiofury/system/restart')
    async def fury_restart(request):
        print(f"\n🔄 [{EXTENSION_NAME}] Reiniciando servidor...")
        sys.stdout.flush()
        # Esta instrucción reinicia Python completamente
        os.execv(sys.executable, [sys.executable] + sys.argv)

except Exception as e:
    print(f"⚠️ Error cargando APIs de sistema: {e}")

# ==============================================================================
#  2. INSTALADOR DE ASSETS
# ==============================================================================
WEB_DIRECTORY = "./interface/js"

def install_web_assets():
    try:
        current_dir = os.path.dirname(__file__)
        js_folder = os.path.join(current_dir, "js")
        comfy_path = os.path.dirname(folder_paths.__file__)
        dest_folder = os.path.join(comfy_path, "web", "extensions", EXTENSION_NAME)

        if os.path.exists(js_folder):
            if not os.path.exists(dest_folder): os.makedirs(dest_folder)
            for file in os.listdir(js_folder):
                if file.endswith(".js") or file.endswith(".css"):
                    src = os.path.join(js_folder, file)
                    dst = os.path.join(dest_folder, file)
                    if not os.path.exists(dst) or not filecmp.cmp(src, dst):
                        shutil.copy(src, dst)
                        if DEBUG_MODE: print(f"⚡ Asset actualizado: {file}")
    except Exception:
        pass

# ==============================================================================
#  3. CARGADOR INTELIGENTE (RECURSIVO + AUTO-REGISTRO)
# ==============================================================================
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

def load_nodes():
    print(f"\n🧩 [{EXTENSION_NAME}] Iniciando búsqueda profunda de nodos...")

    # Recorremos todo el directorio recursivamente
    for root, dirs, files in os.walk(node_root):
        # Ignorar carpetas ocultas o de cache
        if "__pycache__" in root or ".git" in root: continue

        for file in files:
            if file.endswith(".py") and file not in IGNORE_FILES:
                module_path = os.path.join(root, file)
                module_name = os.path.splitext(file)[0]

                try:
                    # Cargar módulo
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    nodes_in_file = 0

                    # A. Si el archivo ya tiene mapeos, úsalos
                    if hasattr(module, "NODE_CLASS_MAPPINGS"):
                        for name, cls in module.NODE_CLASS_MAPPINGS.items():
                            NODE_CLASS_MAPPINGS[name] = cls
                            nodes_in_file += 1
                        if hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS"):
                            NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)

                    # B. Si NO tiene mapeos, búscalos automáticamente (Introspección)
                    else:
                        for name, obj in inspect.getmembers(module):
                            if inspect.isclass(obj):
                                # Verificamos si parece un nodo de ComfyUI
                                if hasattr(obj, "INPUT_TYPES") and hasattr(obj, "RETURN_TYPES"):
                                    # Evitar registrar clases importadas de otros sitios
                                    if obj.__module__ == module.__name__:
                                        # Registrar
                                        key_name = name
                                        NODE_CLASS_MAPPINGS[key_name] = obj

                                        # Crear nombre bonito
                                        fancy_name = "🧩 SF " + name.replace("SF_", "").replace("_", " ")
                                        NODE_DISPLAY_NAME_MAPPINGS[key_name] = fancy_name

                                        nodes_in_file += 1
                                        if DEBUG_MODE: print(f"   🪄 Auto-registrado: {fancy_name}")

                    if nodes_in_file > 0 and DEBUG_MODE:
                        print(f"   ✅ {file}: {nodes_in_file} nodos activos.")

                except Exception as e:
                    print(f"   ❌ Error en {file}: {e}")
                    # traceback.print_exc() # Descomentar para ver error detallado

# ==============================================================================
#  EJECUCIÓN
# ==============================================================================
install_web_assets()
load_nodes()

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]