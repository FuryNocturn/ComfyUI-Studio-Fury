import os
import sys

# --- FIX DE IMPORTACIÓN ---
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(current_dir)
if project_root not in sys.path: sys.path.append(project_root)
from core.sf_io import FuryFileManager
# --------------------------

class SF_ProjectManager:
    """
    El 'Manager' ahora crea un bus de datos (SF_LINK) con toda la info del proyecto.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_name": ("STRING", {"default": "NewMovie", "multiline": False}),
            },
            "optional": {
                "protag_1": ("STRING", {"default": "Hero", "multiline": False}),
                "protag_2": ("STRING", {"default": "", "multiline": False}),
                "protag_3": ("STRING", {"default": "", "multiline": False}),
                "scene_1": ("STRING", {"default": "Main_Loc", "multiline": False}),
                "scene_2": ("STRING", {"default": "", "multiline": False}),
            }
        }

    RETURN_TYPES = ("SF_LINK",)
    RETURN_NAMES = ("fury_bus",)
    FUNCTION = "create_bus"
    CATEGORY = "🧩 Studio Fury/📦 Dataset"

    def create_bus(self, project_name, protag_1, protag_2, protag_3, scene_1, scene_2):
        # Creamos la estructura de carpetas fisica
        FuryFileManager.get_project_root(project_name)

        # Creamos el Paquete de Datos (El Bus)
        # Esto viajará por todos los cables
        bus = {
            "project_name": project_name,
            "entities": {
                "protag_1": {"name": protag_1, "type": "character", "prompts": {}},
                "protag_2": {"name": protag_2, "type": "character", "prompts": {}},
                "protag_3": {"name": protag_3, "type": "character", "prompts": {}},
                "scene_1":  {"name": scene_1,  "type": "scene", "prompts": {}},
                "scene_2":  {"name": scene_2,  "type": "scene", "prompts": {}}
            }
        }

        # Filtramos los vacíos
        bus["entities"] = {k: v for k, v in bus["entities"].items() if v["name"].strip() != ""}

        return (bus,)

NODE_CLASS_MAPPINGS = { "SF_ProjectManager": SF_ProjectManager }
NODE_DISPLAY_NAME_MAPPINGS = { "SF_ProjectManager": "🧠 SF Manager (Data Bus)" }
