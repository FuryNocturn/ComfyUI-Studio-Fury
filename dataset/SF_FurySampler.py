import torch
# Import absoluto
from core.sf_io import fury_common_ksampler

class SF_FurySampler:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "charged_bus": ("SF_LINK",),
                "target_entity_id": ("STRING", {"default": "Hero", "multiline": False}),
                "resolution": (["512x512", "768x768", "1024x1024", "1280x720", "1920x1080"],),
                "steps": ("INT", {"default": 20}),
                "cfg": ("FLOAT", {"default": 8.0}),
                "sampler_name": (["euler", "dpmpp_2m", "dpmpp_sde", "lms"],),
                "scheduler": (["normal", "karras", "simple"],),
                "denoise": ("FLOAT", {"default": 1.0}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = ("SF_LINK", "IMAGE", "LATENT")
    RETURN_NAMES = ("bus_result", "image", "latent")
    FUNCTION = "generate"
    CATEGORY = "🧩 Studio Fury/📦 Dataset"

    def generate(self, model, charged_bus, target_entity_id, resolution, steps, cfg, sampler_name, scheduler, denoise, seed):
        bus = charged_bus.copy()

        vae = bus.get("runtime", {}).get("vae")
        if vae is None:
            raise ValueError("❌ Error: VAE no encontrado en el Bus.")

        target_key = target_entity_id.strip()
        if target_key not in bus.get("entities", {}):
            print(f"⚠️ Entidad '{target_key}' no encontrada.")
            return (bus, torch.zeros(1,512,512,3), {"samples": torch.zeros([1,4,64,64])})

        entity_data = bus["entities"][target_key]

        w, h = map(int, resolution.split('x'))
        latent_image = {"samples": torch.zeros([1, 4, h // 8, w // 8])}

        print(f"🎨 [Sampler] Generando '{target_key}'...")
        samples = fury_common_ksampler(
            model, seed, steps, cfg, sampler_name, scheduler,
            entity_data["cond_pos"], entity_data["cond_neg"],
            latent_image, denoise=denoise
        )[0]

        image = vae.decode(samples["samples"])

        bus["current_render"] = {
            "entity_key": target_key,
            "entity_name": entity_data["name"],
            "type": entity_data["type"],
            "image": image,
            "latent": samples
        }

        return (bus, image, samples)

        # --- REGISTRO DEL NODO ---
        NODE_CLASS_MAPPINGS = {
            "SF_FurySampler": SF_FurySampler
        }
        NODE_DISPLAY_NAME_MAPPINGS = {
            "SF_FurySampler": "🎨 SF Fury Sampler (Test)"
        }