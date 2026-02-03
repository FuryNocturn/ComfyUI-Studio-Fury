import torch
import nodes

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
        # Usamos el VAE Encode estándar pero internamente
        # composed_image shape: [1, H, W, 3]

        # Necesitamos asegurarnos de que la imagen tiene el formato correcto para el VAE
        # El VAE espera [B, C, H, W] en algunos contextos internos, pero el nodo standard VAEEncode usa la imagen tal cual.
        # Invocamos la lógica de codificación:
        t = vae.encode(composed_image[:,:,:,:3])
        original_latent = t.to(composed_image.device) # [1, 4, H/8, W/8]

        # 2. Expansión Temporal (Crear el "Film Strip")
        # Repetimos el latent estático tantas veces como frames queramos
        # Esto crea un video donde, por ahora, todos los frames son iguales.
        video_latents = original_latent.repeat(frame_count, 1, 1, 1)

        # 3. Preparación de la Máscara de Movimiento
        # La máscara viene como [1, H, W]. Necesitamos bajarla a la resolución del Latent (H/8, W/8)
        mask = fusion_mask.clone()

        # Redimensionar máscara al tamaño Latent (nearest para mantener bordes duros o bilinear para suaves)
        # Torch espera [Batch, Channels, Height, Width] para interpolar
        mask = mask.unsqueeze(0) # [1, 1, H, W]

        # Calculamos dimensiones del latent
        lat_h = original_latent.shape[2]
        lat_w = original_latent.shape[3]

        mask_resized = torch.nn.functional.interpolate(
            mask, size=(lat_h, lat_w), mode="bilinear", align_corners=False
        )

        # 4. Aplicar "Motion Freedom" (Libertad de Movimiento)
        # Si la máscara es blanca (1.0), el personaje se mueve.
        # Si es negra (0.0), el fondo está bloqueado.
        # 'motion_freedom' puede hacer que el área "permitida" sea un poco más gris si queremos restringir
        mask_resized = mask_resized * motion_freedom

        # Aplanar para formato de máscara de Comfy [Batch, H, W] (sin canales)
        mask_final = mask_resized.squeeze(1)

        # Repetir la máscara para cada frame del video
        mask_batch = mask_final.repeat(frame_count, 1, 1)

        # 5. Inyectar la máscara en el Latent
        # ComfyUI usa una estructura de diccionario para los latents
        output_latent = {
            "samples": video_latents,
            "noise_mask": mask_batch # Aquí está el secreto del control absoluto
        }

        return (output_latent,)

NODE_CLASS_MAPPINGS = {
    "SF_ActionAnimator": SF_ActionAnimator
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SF_ActionAnimator": "🎬 SF Action Animator (Latent Prep)"
}