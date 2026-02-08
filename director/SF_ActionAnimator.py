import torch

class SF_ActionAnimator:
    """
    Convierte una composición estática en un flujo de video (Latent Batch).
    Aplica 'Movement Restriction' usando la máscara para garantizar que el fondo no tiemble.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "vae": ("VAE",),                # Necesario para codificar la imagen a Latent
                "composed_image": ("IMAGE",),   # La imagen del SceneComposer
                "fusion_mask": ("MASK",),       # La máscara del SceneComposer
                "frame_count": ("INT", {"default": 24, "min": 8, "max": 120, "step": 8}),
                "motion_freedom": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 1.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("LATENT",)
    RETURN_NAMES = ("video_latents",)
    FUNCTION = "prepare_action"
    CATEGORY = "🧩 Studio Fury/🎬 Director"

    def prepare_action(self, vae, composed_image, fusion_mask, frame_count, motion_freedom):
        # 1. Codificación VAE (De Píxeles a Latents)
        # ComfyUI espera [Batch, H, W, C]
        # VAE Encode output -> {"samples": tensor}

        print(f"🎬 [Animator] Codificando {frame_count} frames...")

        # Codificamos la imagen compuesta
        encoded = vae.encode(composed_image[:,:,:,:3]) # Asegurar 3 canales
        original_latent = encoded["samples"] # [1, 4, H/8, W/8]

        # 2. Repetición temporal (Batch Repeat)
        # Convertimos 1 imagen estática en N frames idénticos
        video_latents = original_latent.repeat(frame_count, 1, 1, 1)

        # 3. Procesamiento de la Máscara
        # La máscara viene como [H, W] o [1, H, W]
        mask = fusion_mask
        if len(mask.shape) == 2:
            mask = mask.unsqueeze(0)

        # Escalar máscara al tamaño del latent (1/8)
        # Necesitamos [1, 1, H, W] para interpolación
        mask_tensor = mask.unsqueeze(0)

        # Dimensiones objetivo
        lat_h = original_latent.shape[2]
        lat_w = original_latent.shape[3]

        mask_resized = torch.nn.functional.interpolate(
            mask_tensor, size=(lat_h, lat_w), mode="bilinear", align_corners=False
        )

        # Quitar dimensiones extra -> [1, H, W]
        mask_resized = mask_resized.squeeze(0)

        # 4. Aplicar "Motion Freedom"
        # 1.0 = Movimiento total donde hay máscara.
        # 0.0 = Congelado.
        mask_final = mask_resized * motion_freedom

        # Repetir máscara para cada frame
        mask_batch = mask_final.repeat(frame_count, 1, 1)

        # 5. Salida en formato Latent de ComfyUI
        # Inyectamos la 'noise_mask'. Los samplers de video (AnimateDiff) la usan
        # para saber qué píxeles deben cambiar y cuáles dejar quietos.
        output_latent = {
            "samples": video_latents,
            "noise_mask": mask_batch
        }

        return (output_latent,)

# --- REGISTRO DEL NODO ---
NODE_CLASS_MAPPINGS = {
    "SF_ActionAnimator": SF_ActionAnimator
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "SF_ActionAnimator": "🏃 SF Action Animator"
}