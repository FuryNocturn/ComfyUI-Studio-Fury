import os
import torch
import folder_paths
import nodes
import sys
import numpy as np
from PIL import Image

# Extensión para archivos de datos (Tensores)
FURY_EXT = ".fury"

class FuryFileManager:
    """
    Gestor centralizado de Archivos I/O.
    """
    @staticmethod
    def get_project_root(project_name):
        output_dir = folder_paths.get_output_directory()
        project_path = os.path.join(output_dir, "StudioFury", project_name)
        
        if not os.path.exists(project_path):
            try:
                os.makedirs(project_path, exist_ok=True)
                # Subcarpetas estándar
                for folder in ["Characters", "Scenes", "Renders", "Cache"]:
                    os.makedirs(os.path.join(project_path, folder), exist_ok=True)
                print(f"✨ [StudioFury] Estructura creada: {project_path}")
            except Exception as e:
                print(f"❌ [StudioFury] Error IO: {e}")
        return project_path

    @staticmethod
    def save_fury_asset(project_name, subfolder, asset_name, data_dict):
        """Guarda los datos técnicos (Tensores/Latents)"""
        root = FuryFileManager.get_project_root(project_name)
        file_path = os.path.join(root, subfolder, f"{asset_name}{FURY_EXT}")
        torch.save(data_dict, file_path)
        print(f"💾 [Data] Guardado: {asset_name}{FURY_EXT}")
        return file_path

    @staticmethod
    def save_preview_png(project_name, subfolder, asset_name, tensor_image):
        """
        Guarda un PNG visible para que el usuario vea el archivo en Windows/Mac.
        """
        try:
            root = FuryFileManager.get_project_root(project_name)
            
            # Convertir Tensor [1, H, W, C] a Numpy
            i = 255. * tensor_image.cpu().numpy()
            img_numpy = np.clip(i, 0, 255).astype(np.uint8)
            
            # Quitar dimensión batch
            if img_numpy.shape[0] == 1:
                img_numpy = img_numpy[0]
            
            # Guardar con Pillow
            img_pil = Image.fromarray(img_numpy)
            file_path = os.path.join(root, subfolder, f"{asset_name}.png")
            img_pil.save(file_path, compress_level=4)
            print(f"🖼️ [View] Preview generada: {asset_name}.png")
            
        except Exception as e:
            print(f"⚠️ Error generando PNG sidecar: {e}")

    @staticmethod
    def load_fury_asset(project_name, subfolder, asset_name):
        root = FuryFileManager.get_project_root(project_name)
        candidates = [
            os.path.join(root, subfolder, f"{asset_name}{FURY_EXT}"),
            os.path.join(root, subfolder, asset_name)
        ]
        for path in candidates:
            if os.path.exists(path):
                try:
                    return torch.load(path)
                except Exception as e:
                    print(f"❌ Error cargando {asset_name}: {e}")
                    return None
        return None

# Wrapper seguro para KSampler
def fury_common_ksampler(model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent, denoise=1.0):
    try:
        return nodes.common_ksampler(model, seed, steps, cfg, sampler_name, scheduler, positive, negative, latent, denoise=denoise)
    except Exception as e:
        print(f"❌ [FurySampler] Error crítico en sampling: {e}")
        return latent