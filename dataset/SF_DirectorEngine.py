import torch
import os
import sys
import nodes
import random
import folder_paths

# --- FIX IMPORT ---
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(current_dir)
if project_root not in sys.path: sys.path.append(project_root)
from core.sf_io import FuryFileManager
# ------------------

class SF_DirectorEngine:
    """
    V5: Visor limpio. Muestra las imágenes en su tamaño original sin agregar bordes negros.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "vae": ("VAE",),
                "charged_bus": ("SF_LINK",),
                "quality_preset": (["SD (512px)", "HD (720px)", "Full HD (1080px)", "2K (1440px)", "4K (2160px)"],),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "steps": ("INT", {"default": 25}),
                "cfg": ("FLOAT", {"default": 8.0}),
                "sampler_name": (nodes.comfy.samplers.KSampler.SAMPLERS, ),
                "scheduler": (nodes.comfy.samplers.KSampler.SCHEDULERS, ),
                "denoise": ("FLOAT", {"default": 1.0}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("last_image",)
    OUTPUT_NODE = True
    FUNCTION = "run_director"
    CATEGORY = "🧩 Studio Fury/📦 Dataset"

    def run_director(self, model, vae, charged_bus, quality_preset, seed, steps, cfg, sampler_name, scheduler, denoise):

        project_name = charged_bus["project_name"]
        entities = charged_bus["entities"]

        # --- RESOLUCIÓN ---
        if "SD" in quality_preset: base_size = 512
        elif "HD" in quality_preset: base_size = 720
        elif "1080" in quality_preset: base_size = 1080
        elif "2K" in quality_preset: base_size = 1440
        else: base_size = 2160

        print(f"🎬 [Director] Batch Start | Base: {base_size}px")

        from nodes import common_ksampler, PreviewImage

        processed_count = 0
        ui_results = [] # Lista para el visor de la UI
        last_tensor = None

        # BUCLE
        for key, data in entities.items():
            print(f"   👉 Generando: {data['name']} ({data['type']})...")

            # 1. Geometría
            if data["type"] == "character":
                w, h = base_size, int(base_size * 1.5)
            else:
                w, h = int(base_size * 1.5), base_size

            w, h = (w // 8) * 8, (h // 8) * 8

            latent = torch.zeros([1, 4, h // 8, w // 8])
            latent_image = {"samples": latent}

            # 2. Conditioning
            positive = data["cond_pos"]
            negative = data["cond_neg"]

            # 3. Generar
            try:
                samples = common_ksampler(model, seed + processed_count, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise=denoise)[0]
                image = vae.decode(samples["samples"])

                # 4. Guardar Asset (Definitivo)
                folder_type = "Characters" if data["type"] == "character" else "Scenes"
                asset_data = {
                    "type": data["type"], "version": "2.0", "name": data["name"],
                    "preview_image": image, "latent": samples
                }
                FuryFileManager.save_fury_asset(project_name, folder_type, data["name"], asset_data)

                # 5. PREPARAR VISOR (Sin bordes negros)
                # Usamos PreviewImage para guardar este frame específico en temp
                # y obtener su metadato UI correcto.
                saved_info = PreviewImage().save_images(image)
                if "ui" in saved_info and "images" in saved_info["ui"]:
                    ui_results.extend(saved_info["ui"]["images"])

                last_tensor = image
                processed_count += 1

            except Exception as e:
                print(f"      ❌ Error generando {data['name']}: {e}")

        # --- RETORNO FINAL ---
        # Devolvemos la lista de imágenes limpia a la UI.
        # Por el cable (output) solo mandamos la última para evitar errores de tamaño mixto en nodos siguientes.

        if last_tensor is None:
            last_tensor = torch.zeros(1, 512, 512, 3)

        print(f"🏁 [Director] Terminado. {processed_count} assets.")

        return {
            "ui": {"images": ui_results},
            "result": (last_tensor,)
        }

NODE_CLASS_MAPPINGS = { "SF_DirectorEngine": SF_DirectorEngine }
NODE_DISPLAY_NAME_MAPPINGS = { "SF_DirectorEngine": "3️⃣ SF Director (Clean View)" }