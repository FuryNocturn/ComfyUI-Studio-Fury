import torch
import nodes
import gc
# Import absoluto
from core.sf_io import FuryFileManager, fury_common_ksampler

class SF_DirectorEngine:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL",),
                "charged_bus": ("SF_LINK",),
                "quality_preset": (["SD (512px)", "HD (720px)", "Full HD (1080px)", "2K (1440px)", "4K (2160px)"],),
                "steps": ("INT", {"default": 25}),
                "cfg": ("FLOAT", {"default": 8.0}),
                "sampler_name": (nodes.comfy.samplers.KSampler.SAMPLERS, ),
                "scheduler": (nodes.comfy.samplers.KSampler.SCHEDULERS, ),
                "denoise": ("FLOAT", {"default": 1.0}),
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("last_image",)
    OUTPUT_NODE = True
    FUNCTION = "run_director"
    CATEGORY = "🧩 Studio Fury/🎬 Director"

    def run_director(self, model, charged_bus, quality_preset, steps, cfg, sampler_name, scheduler, denoise, seed):
        project_name = charged_bus.get("project_name", "Untitled")
        entities = charged_bus.get("entities", {})
        vae = charged_bus.get("runtime", {}).get("vae")

        if not entities: return {"ui": {"images": []}, "result": (torch.zeros(1,512,512,3),)}
        if not vae: raise ValueError("❌ El VAE no está en el Bus.")

        base_size = 512
        if "HD" in quality_preset: base_size = 720
        elif "1080" in quality_preset: base_size = 1080
        elif "2K" in quality_preset: base_size = 1440
        elif "4K" in quality_preset: base_size = 2160

        print(f"🎬 [Director] Iniciando Batch: {len(entities)} activos | Base: {base_size}px")

        from nodes import PreviewImage
        previewer = PreviewImage()
        ui_results = []
        last_tensor = None
        processed_count = 0

        for i, (key, data) in enumerate(entities.items()):
            print(f"   👉 Generando: {data['name']}...")

            ratio_tag = data.get("ratio_tag", "square")
            if data["type"] == "character" or ratio_tag == "character_sheet":
                width = int(base_size * 0.66)
                height = base_size
                if base_size < 1000: height = int(base_size * 1.5)
            else:
                mult = 1.0
                is_landscape = True
                if "16:9" in ratio_tag: mult = 1.77
                elif "21:9" in ratio_tag: mult = 2.33
                elif "1.90" in ratio_tag: mult = 1.90
                elif "9:16" in ratio_tag: mult = 1.77; is_landscape = False

                if is_landscape: height = base_size; width = int(base_size * mult)
                else: width = base_size; height = int(base_size * mult)

            width = (width // 8) * 8
            height = (height // 8) * 8

            try:
                latent = {"samples": torch.zeros([1, 4, height // 8, width // 8])}
                current_seed = seed + i
                samples = fury_common_ksampler(
                    model, current_seed, steps, cfg, sampler_name, scheduler,
                    data["cond_pos"], data["cond_neg"], latent, denoise=denoise
                )[0]

                image = vae.decode(samples["samples"])

                folder = "Characters" if data["type"] == "character" else "Scenes"
                asset_data = {"version": "3.0", "type": data["type"], "name": data["name"], "image": image, "latent": samples}

                FuryFileManager.save_fury_asset(project_name, folder, data["name"], asset_data)
                FuryFileManager.save_preview_png(project_name, folder, data["name"], image)

                saved_info = previewer.save_images(image)
                if "ui" in saved_info: ui_results.extend(saved_info["ui"]["images"])

                last_tensor = image
                processed_count += 1

                del image, samples, latent
                gc.collect()
                torch.cuda.empty_cache()

            except Exception as e:
                print(f"      ❌ Error en {data['name']}: {e}")

        if last_tensor is None: last_tensor = torch.zeros(1, 512, 512, 3)
        return {"ui": {"images": ui_results}, "result": (last_tensor,)}

        # --- REGISTRO DEL NODO ---
        NODE_CLASS_MAPPINGS = {
            "SF_DirectorEngine": SF_DirectorEngine
        }
        NODE_DISPLAY_NAME_MAPPINGS = {
            "SF_DirectorEngine": "3️⃣ SF Director Engine (Batch)"
        }