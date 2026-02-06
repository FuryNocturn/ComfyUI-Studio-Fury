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
    Sampler Manual. Permite seleccionar una entidad específica del bus y generarla.
    Compatible con el sistema 'Smart Layers' del Prompt Engine.
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
                # Selector manual de qué quieres generar ahora mismo
                "target_entity": (["P1", "P2", "S1", "S2"],),
                "resolution": (["512x512", "768x768", "512x768", "768x512", "1024x1024", "1280x720", "1920x1080"],),
                "steps": ("INT", {"default": 20, "min": 1, "max": 100}),
                "cfg": ("FLOAT", {"default": 8.0, "min": 0.0, "max": 100.0}),
                "sampler_name": (nodes.comfy.samplers.KSampler.SAMPLERS, ),
                "scheduler": (nodes.comfy.samplers.KSampler.SCHEDULERS, ),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "denoise": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0}),
            }
        }

    RETURN_TYPES = ("SF_LINK", "IMAGE", "LATENT")
    RETURN_NAMES = ("fury_bus", "preview_image", "raw_latent")
    FUNCTION = "generate"
    CATEGORY = "🧩 Studio Fury/📦 Dataset"

    def generate(self, model, vae, charged_bus, target_entity, resolution, steps, cfg, sampler_name, scheduler, seed, denoise):

        # 1. Clonamos el bus para no romper nada
        bus = charged_bus.copy()

        # 2. Verificar si la entidad existe en el Manager
        if target_entity not in bus["entities"]:
            print(f"⚠️ [FurySampler] La entidad {target_entity} no está definida o está vacía.")
            # Retorno de seguridad (imagen negra)
            empty_img = torch.zeros(1, 512, 512, 3)
            empty_lat = {"samples": torch.zeros(1, 4, 64, 64)}
            return (bus, empty_img, empty_lat)

        entity_data = bus["entities"][target_entity]
        print(f"🎨 [Manual Mode] Generando: {entity_data['name']}...")

        # 3. Recuperar Conditioning (ACTUALIZADO para Smart Layers)
        # Antes buscábamos en "prompts", ahora están en "cond_pos" y "cond_neg"
        if "cond_pos" not in entity_data:
            raise ValueError(f"Falta procesar los prompts para {entity_data['name']}. Revisa el Prompt Engine.")

        positive = entity_data["cond_pos"]
        negative = entity_data["cond_neg"]

        # 4. Configurar Latent
        w, h = map(int, resolution.split('x'))
        latent = torch.zeros([1, 4, h // 8, w // 8])
        latent_image = {"samples": latent}

        # 5. Sampling
        from nodes import common_ksampler
        samples = common_ksampler(model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent_image, denoise=denoise)[0]

        # 6. Decode
        image = vae.decode(samples["samples"])

        # 7. Preparamos el paquete para el SmartSaver
        bus["current_render"] = {
            "entity_key": target_entity,
            "entity_name": entity_data["name"],
            "type": entity_data["type"],
            "latent": samples,
            "image": image
        }

        return (bus, image, samples)

NODE_CLASS_MAPPINGS = { "SF_FurySampler": SF_FurySampler }
NODE_DISPLAY_NAME_MAPPINGS = { "SF_FurySampler": "✨ Fury Manual Sampler" }