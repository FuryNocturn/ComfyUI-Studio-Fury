import os
import sys
import torch

# --- FIX IMPORT ---
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(current_dir)
if project_root not in sys.path: sys.path.append(project_root)
from core.sf_io import FuryFileManager
# ------------------

class SF_SmartSaver:
    """
    Recibe el Bus del Sampler. Si 'save_action' es True, guarda el activo
    en la carpeta correcta automáticamente.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "fury_bus": ("SF_LINK",),
                "save_action": ("BOOLEAN", {"default": False, "label_on": "💾 SAVE", "label_off": "👀 PREVIEW ONLY"}),
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "smart_save"
    OUTPUT_NODE = True
    CATEGORY = "🧩 Studio Fury/📦 Dataset"

    def smart_save(self, fury_bus, save_action):
        if not save_action:
            print("👀 [FurySaver] Modo Preview. No se guardó nada.")
            return {}

        if "current_render" not in fury_bus:
            print("❌ [FurySaver] No hay render en el bus.")
            return {}

        render_data = fury_bus["current_render"]
        project_name = fury_bus["project_name"]

        # Determinar carpeta según tipo
        folder_type = "Characters" if render_data["type"] == "character" else "Scenes"

        # Preparar paquete .fury
        asset_data = {
            "type": render_data["type"],
            "version": "2.0",
            "name": render_data["entity_name"],
            "preview_image": render_data["image"],
            "latent": render_data["latent"]
        }

        # Guardar usando el Core
        FuryFileManager.save_fury_asset(project_name, folder_type, render_data["entity_name"], asset_data)

        return {}

NODE_CLASS_MAPPINGS = { "SF_SmartSaver": SF_SmartSaver }
NODE_DISPLAY_NAME_MAPPINGS = { "SF_SmartSaver": "💾 Smart Saver (Auto-Path)" }