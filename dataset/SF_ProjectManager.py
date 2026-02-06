import os
import sys

# --- FIX IMPORT ---
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(current_dir)
if project_root not in sys.path: sys.path.append(project_root)
from core.sf_io import FuryFileManager
# ------------------

class SF_ProjectManager:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_name": ("STRING", {"default": "MyMovie_01"}),
            },
            "optional": {
                # Campos fijos. Si están vacíos, se ignoran.
                "protag_1_name": ("STRING", {"default": "Hero"}),
                "protag_2_name": ("STRING", {"default": ""}),
                "scene_1_name": ("STRING", {"default": "Main_Loc"}),
                "scene_2_name": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("SF_LINK",)
    RETURN_NAMES = ("fury_bus",)
    FUNCTION = "create_bus"
    CATEGORY = "🧩 Studio Fury/📦 Dataset"

    def create_bus(self, project_name, protag_1_name, protag_2_name, scene_1_name, scene_2_name):
        FuryFileManager.get_project_root(project_name)

        # Estructura limpia. Solo añadimos lo que tiene nombre.
        entities = {}

        if protag_1_name.strip():
            entities["P1"] = {"name": protag_1_name, "type": "character"}
        if protag_2_name.strip():
            entities["P2"] = {"name": protag_2_name, "type": "character"}

        if scene_1_name.strip():
            entities["S1"] = {"name": scene_1_name, "type": "scene"}
        if scene_2_name.strip():
            entities["S2"] = {"name": scene_2_name, "type": "scene"}

        bus = {
            "project_name": project_name,
            "entities": entities
        }

        print(f"🧠 [SF Manager] Entidades activas: {list(entities.keys())}")
        return (bus,)

NODE_CLASS_MAPPINGS = { "SF_ProjectManager": SF_ProjectManager }
NODE_DISPLAY_NAME_MAPPINGS = { "SF_ProjectManager": "1️⃣ SF Manager (Definir)" }