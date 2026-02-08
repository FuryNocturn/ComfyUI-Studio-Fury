import os
import sys
# Import absoluto (gracias al fix en __init__.py)
from core.sf_io import FuryFileManager

class SF_ProjectManager:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip": ("CLIP",),
                "vae": ("VAE",),
                "project_name": ("STRING", {"default": "My_Epic_Movie", "multiline": False}),
            }
        }

    RETURN_TYPES = ("SF_LINK",)
    RETURN_NAMES = ("bus",)
    FUNCTION = "init_project"
    CATEGORY = "🧩 Studio Fury/📦 Dataset"

    def init_project(self, clip, vae, project_name):
        root_path = FuryFileManager.get_project_root(project_name)
        bus = {
            "project_name": project_name,
            "project_root": root_path,
            "entities": {},
            "runtime": {
                "clip": clip,
                "vae": vae
            }
        }
        print(f"🎬 [ProjectManager] Proyecto '{project_name}' iniciado.")
        return (bus,)

        # --- REGISTRO DEL NODO ---
        NODE_CLASS_MAPPINGS = {
            "SF_ProjectManager": SF_ProjectManager
        }
        NODE_DISPLAY_NAME_MAPPINGS = {
            "SF_ProjectManager": "1️⃣ SF Project Manager (Start)"
        }