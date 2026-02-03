import torch
import os
import sys
import nodes # Importamos nodos estandar de ComfyUI para usar su KSampler internamente

# --- FIX IMPORT ---
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(current_dir)
if project_root not in sys.path: sys.path.append(project_root)
# ------------------

class SF_FurySampler:
    """
    Sampler todo-en-uno. Selecciona resolución y Entidad del Bus.
    Genera la imagen y pasa los datos al Saver.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "vae": ("VAE",),
                "charged_bus": ("SF_LINK",), # El bus que viene del Prompt Engine
                "target_entity": (["protag_1", "protag_2", "protag_3", "scene_1", "scene_2"],),
                "resolution": (["512x512", "768x768", "512x768", "768x512", "1024x1024", "1280x720", "1920x1080"],),
                "steps": ("INT", {"default": 20, "min": 1, "max": 100}),
                "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0}),
                "sampler_name": (nodes.comfy.samplers.KSampler.SAMPLERS, ),
                "scheduler": (nodes.comfy.samplers.KSampler.SCHEDULERS, ),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = ("SF_LINK", "IMAGE", "LATENT")
    RETURN_NAMES = ("fury_bus", "preview_image", "raw_latent")
    FUNCTION = "generate"
    CATEGORY = "🧩 Studio Fury/📦 Dataset"

    def generate(self, model, vae, charged_bus, target_entity, resolution, steps, cfg, sampler_name, scheduler, seed):

        # 1. Verificar si la entidad existe en el Bus
        if target_entity not in charged_bus["entities"]:
            print(f"⚠️ [FurySampler] La entidad {target_entity} no está definida en el Manager. Saltando.")
            # Retorno vacío seguro
            empty_img = torch.zeros(1, 512, 512, 3)
            empty_lat = {"samples": torch.zeros(1, 4, 64, 64)}
            return (charged_bus, empty_img, empty_lat)

        entity_data = charged_bus["entities"][target_entity]

        # 2. Recuperar Conditioning del Bus
        if "positive" not in entity_data["prompts"]:
            raise ValueError(f"Falta el prompt positivo para {entity_data['name']}. Úsalo en el Prompt Engine.")

        positive = entity_data["prompts"]["positive"]
        negative = entity_data["prompts"]["negative"]

        # 3. Configurar Latent Vacío según resolución
        w, h = map(int, resolution.split('x'))
        latent = torch.zeros([1, 4, h // 8, w // 8])
        latent_image = {"samples": latent}

        # 4. Invocar al KSampler Estándar
        # Usamos la función común de ComfyUI para muestrear
        from nodes import common_ksampler
        samples = common_ksampler(model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise=1.0)[0]

        # 5. Decodificar VAE para preview
        image = vae.decode(samples["samples"])

        # 6. ACTUALIZAR EL BUS CON EL RESULTADO ACTUAL
        # Esto es clave: el Bus ahora "carga" el resultado para que el Saver sepa qué guardar
        charged_bus["current_render"] = {
            "entity_key": target_entity,
            "entity_name": entity_data["name"],
            "type": entity_data["type"],
            "latent": samples,
            "image": image
        }

        return (charged_bus, image, samples)

NODE_CLASS_MAPPINGS = { "SF_FurySampler": SF_FurySampler }
NODE_DISPLAY_NAME_MAPPINGS = { "SF_FurySampler": "✨ Fury Smart Sampler" }