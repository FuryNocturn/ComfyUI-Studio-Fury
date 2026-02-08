import torch
import os
# Import absoluto
from core.sf_io import FuryFileManager

class SF_AssetLoader:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "project_name": ("STRING", {"default": "My_Movie_01"}),
                "asset_type": (["Characters", "Scenes"],),
                "asset_name": ("STRING", {"default": "Hero_01"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "LATENT")
    RETURN_NAMES = ("image", "latent")
    FUNCTION = "load_asset"
    CATEGORY = "🧩 Studio Fury/🎬 Director"

    def load_asset(self, project_name, asset_type, asset_name):
        data = FuryFileManager.load_fury_asset(project_name, asset_type, asset_name)

        if data is None:
            empty_img = torch.zeros(1, 512, 512, 3)
            empty_lat = {"samples": torch.zeros([1, 4, 64, 64])}
            return (empty_img, empty_lat)

        image = data.get("image", data.get("preview_image"))
        latent = data.get("latent")

        return (image, latent)

        # --- REGISTRO DEL NODO ---
        NODE_CLASS_MAPPINGS = {
            "SF_AssetLoader": SF_AssetLoader
        }
        NODE_DISPLAY_NAME_MAPPINGS = {
            "SF_AssetLoader": "📂 SF Asset Loader"
        }