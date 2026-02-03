import os
import torch
import json
import folder_paths

# Definimos la extensión y carpetas
FURY_EXT = ".fury"

class FuryFileManager:
    """
    Gestor centralizado de I/O para StudioFury.
    Maneja la creación de carpetas y el guardado de Tensores.
    """

    @staticmethod
    def get_project_root(project_name):
        # Usamos la carpeta output de ComfyUI como base
        output_dir = folder_paths.get_output_directory()
        # Estructura: ComfyUI/output/StudioFury/NombreProyecto
        project_path = os.path.join(output_dir, "StudioFury", project_name)

        # Crear estructura si no existe
        if not os.path.exists(project_path):
            try:
                os.makedirs(project_path, exist_ok=True)
                os.makedirs(os.path.join(project_path, "Characters"), exist_ok=True)
                os.makedirs(os.path.join(project_path, "Scenes"), exist_ok=True)
                os.makedirs(os.path.join(project_path, "Renders"), exist_ok=True)
                print(f"✨ [StudioFury] Nuevo proyecto creado: {project_path}")
            except Exception as e:
                print(f"❌ [StudioFury] Error creando carpetas: {e}")

        return project_path

    @staticmethod
    def save_fury_asset(project_name, subfolder, asset_name, data_dict):
        """
        Guarda un diccionario de tensores en un archivo .fury
        """
        root = FuryFileManager.get_project_root(project_name)
        file_path = os.path.join(root, subfolder, f"{asset_name}{FURY_EXT}")

        # Guardado nativo de Torch (mantiene gradientes y precisión)
        torch.save(data_dict, file_path)
        print(f"💾 [StudioFury] Asset guardado: {asset_name} -> {file_path}")
        return file_path

    @staticmethod
    def load_fury_asset(project_name, subfolder, asset_name):
        """
        Carga y devuelve el diccionario de datos.
        """
        root = FuryFileManager.get_project_root(project_name)
        file_path = os.path.join(root, subfolder, f"{asset_name}{FURY_EXT}")

        if not os.path.exists(file_path):
            # Intento de búsqueda fallback (por si ponen la extensión manual)
            if not os.path.exists(file_path) and not asset_name.endswith(FURY_EXT):
                 file_path = os.path.join(root, subfolder, f"{asset_name}")

        if not os.path.exists(file_path):
            print(f"❌ [StudioFury] Archivo no encontrado: {file_path}")
            return None

        print(f"📂 [StudioFury] Cargando: {asset_name}")
        return torch.load(file_path)
