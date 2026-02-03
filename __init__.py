import os
import shutil
import importlib
import importlib.util
import traceback
import folder_paths
import filecmp
# --- NUEVOS IMPORTS NECESARIOS PARA EL BOTÓN DE APAGADO ---
from server import PromptServer
from aiohttp import web

# ==============================================================================
# CONFIGURACIÓN DEL SISTEMA
# ==============================================================================

EXTENSION_NAME = "StudioFury"
# Asegúrate de que estas carpetas existan o el sistema dará error al cargar
NODE_CATEGORIES = ["prompts", "dataset", "director"] # Añade aquí tus categorías futuras (images, utils...)
ASSET_FOLDERS = ["js", "css", "assets", "lib", "fonts"]
DEBUG_MODE = True

# ==============================================================================
# PARTE 1: API DE APAGADO (KILL SWITCH)
# Esta función escucha la petición del botón rojo y cierra Python.
# ==============================================================================
try:
    routes = PromptServer.instance.routes

    @routes.post('/studiofury/system/shutdown')
    async def fury_shutdown(request):
        """
        Recibe la orden del navegador y mata el proceso de Python inmediatamente.
        """
        print("\n🛑 [StudioFury] Recibida orden de apagado. Cerrando sistema...")

        # Preparamos una respuesta rápida
        resp = web.Response(text="Server Killed")

        # Forzamos el cierre del proceso inmediatamente
        os._exit(0)

        return resp
except Exception as e:
    print(f"⚠️ [StudioFury] No se pudo cargar la API de apagado (¿Quizás ComfyUI está desactualizado?): {e}")

# ==============================================================================
# PARTE 2: GESTOR DE ASSETS (Frontend / Javascript)
# Mantiene la estructura de carpetas original para evitar conflictos de nombres.
# ==============================================================================
def install_web_assets():
    root_dir = os.path.dirname(os.path.realpath(__file__))

    # Destino base: ComfyUI/web/extensions/StudioFury
    comfy_path = os.path.dirname(folder_paths.__file__)
    dest_root = os.path.join(comfy_path, "web", "extensions", EXTENSION_NAME)

    # Limpieza preventiva (opcional, pero recomendada para evitar basura vieja)
    # Si prefieres no borrar todo cada vez, puedes comentar estas líneas,
    # pero ayuda a eliminar archivos que hayas borrado en tu proyecto.
    if os.path.exists(dest_root):
        # Solo borramos si estamos seguros de que es nuestra carpeta
        pass

    print(f"📦 [StudioFury] Escaneando assets jerárquicos...")

    copied_count = 0

    # Recorremos el proyecto
    for root, dirs, files in os.walk(root_dir):
        # Filtros de seguridad
        if "__pycache__" in root or ".git" in root or "web/extensions" in root:
            continue

        # Revisamos las subcarpetas de la ruta actual
        for dir_name in dirs:
            # Si encontramos una carpeta de assets (js, css, etc.)
            if dir_name in ASSET_FOLDERS:
                source_folder = os.path.join(root, dir_name)

                # --- LA MAGIA: Calculamos la ruta relativa ---
                # Esto convierte "C:/.../StudioFury/prompts/js" en "prompts/js"
                relative_path = os.path.relpath(source_folder, root_dir)

                # Creamos el destino manteniendo esa ruta: ".../extensions/StudioFury/prompts/js"
                target_folder = os.path.join(dest_root, relative_path)

                if not os.path.exists(target_folder):
                    os.makedirs(target_folder)

                # Copiamos los archivos
                for file in os.listdir(source_folder):
                    src_file = os.path.join(source_folder, file)
                    dst_file = os.path.join(target_folder, file)

                    # Solo archivos, ignoramos sub-subcarpetas por ahora para simplificar
                    if os.path.isfile(src_file):
                        if not os.path.exists(dst_file) or not filecmp.cmp(src_file, dst_file):
                            shutil.copy(src_file, dst_file)
                            copied_count += 1
                            if DEBUG_MODE:
                                print(f"   -> Copiado: {relative_path}/{file}")

    if copied_count > 0:
        print(f"✅ [StudioFury] Actualizados {copied_count} archivos.")

# ==============================================================================
# PARTE 3: CARGADOR DE NODOS (Backend / Python)
# ==============================================================================
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

def load_nodes():
    global NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS
    root_dir = os.path.dirname(os.path.realpath(__file__))

    print(f"\n🚀 [StudioFury] Cargando nodos...")

    for category in NODE_CATEGORIES:
        category_path = os.path.join(root_dir, category)

        if not os.path.exists(category_path):
            continue

        files = os.listdir(category_path)
        for file in files:
            if not file.endswith(".py") or file.startswith("__"):
                continue

            module_name = os.path.splitext(file)[0]
            file_path = os.path.join(category_path, file)

            try:
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                if hasattr(module, "NODE_CLASS_MAPPINGS"):
                    NODE_CLASS_MAPPINGS.update(module.NODE_CLASS_MAPPINGS)
                if hasattr(module, "NODE_DISPLAY_NAME_MAPPINGS"):
                    NODE_DISPLAY_NAME_MAPPINGS.update(module.NODE_DISPLAY_NAME_MAPPINGS)

                if DEBUG_MODE: print(f"   ✅ Nodo cargado: {module_name}")

            except Exception as e:
                if DEBUG_MODE:
                    print(f"\n❌ [StudioFury] ERROR en {module_name}:")
                    traceback.print_exc()
                    print("---------------------------------------------------\n")

# ==============================================================================
# EJECUCIÓN
# ==============================================================================
install_web_assets()
load_nodes()

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]

# NO DEFINIMOS WEB_DIRECTORY.
# Al no definirlo, ComfyUI no intentará sobrescribir tu trabajo.
# Simplemente leerá lo que 'install_web_assets' colocó en web/extensions/StudioFury.