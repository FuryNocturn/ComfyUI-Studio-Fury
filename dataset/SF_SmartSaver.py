import os
import sys
# Import absoluto
from core.sf_io import FuryFileManager

class SF_SmartSaver:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "fury_bus": ("SF_LINK",),
                "save_action": ("BOOLEAN", {"default": True, "label_on": "💾 SAVE", "label_off": "👀 PREVIEW ONLY"}),
            }
        }

    RETURN_TYPES = ()
    FUNCTION = "smart_save"
    OUTPUT_NODE = True
    CATEGORY = "🧩 Studio Fury/📦 Dataset"

    def smart_save(self, fury_bus, save_action):
        if not save_action: return {}
        if "current_render" not in fury_bus: return {}

        render = fury_bus["current_render"]
        project = fury_bus.get("project_name", "Unknown_Project")
        folder = "Scenes" if render["type"] == "scene" else "Characters"

        asset_data = {
            "type": render["type"], "version": "3.0",
            "name": render["entity_name"],
            "image": render["image"], "latent": render["latent"]
        }

        FuryFileManager.save_fury_asset(project, folder, render["entity_name"], asset_data)
        FuryFileManager.save_preview_png(project, folder, render["entity_name"], render["image"])

        return {}

        # --- REGISTRO DEL NODO ---
        NODE_CLASS_MAPPINGS = {
            "SF_SmartSaver": SF_SmartSaver
        }
        NODE_DISPLAY_NAME_MAPPINGS = {
            "SF_SmartSaver": "💾 SF Smart Saver"
        }