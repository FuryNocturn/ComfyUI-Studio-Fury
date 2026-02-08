import torch
import torch.nn.functional as F

class SF_SceneComposer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "scene_image": ("IMAGE",),      # [B, H, W, 3]
                "character_image": ("IMAGE",),  # [B, H, W, 3]
                "x_offset": ("INT", {"default": 0, "min": 0, "max": 4096}),
                "y_offset": ("INT", {"default": 0, "min": 0, "max": 4096}),
                "scale": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 5.0}),
                # Nuevo: Opacidad para fantasmas o integración sutil
                "opacity": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1.0}),
            },
            "optional": {
                 # Nuevo: Máscara real del personaje si existe
                "char_mask": ("MASK",),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("composed_image", "fusion_mask")
    FUNCTION = "compose"
    CATEGORY = "🧩 Studio Fury/🎬 Director"

    def compose(self, scene_image, character_image, x_offset, y_offset, scale, opacity, char_mask=None):
        # Clonamos fondo
        canvas = scene_image.clone()
        B, H, W, C = canvas.shape

        # --- ESCALADO ---
        # Convertimos a [B, C, H, W] para interpolar
        char_tensor = character_image.permute(0, 3, 1, 2)
        target_h = int(character_image.shape[1] * scale)
        target_w = int(character_image.shape[2] * scale)

        char_resized = F.interpolate(char_tensor, size=(target_h, target_w), mode="bilinear")
        char_resized = char_resized.permute(0, 2, 3, 1) # Volver a [B, H, W, C]

        # --- MÁSCARA (ALPHA) ---
        if char_mask is not None:
            # Si el usuario conectó una máscara, la escalamos igual que la imagen
            mask_tensor = char_mask.unsqueeze(0).unsqueeze(0) # [1, 1, H, W]
            mask_resized = F.interpolate(mask_tensor, size=(target_h, target_w), mode="bilinear")
            mask_resized = mask_resized.squeeze(0).squeeze(0) # [H, W]

            # Expandir dimensiones para multiplicar con imagen [H, W, 1]
            alpha = mask_resized.unsqueeze(-1)
        else:
            # Si no hay máscara, creamos una cuadrada completa (1.0)
            alpha = torch.ones((target_h, target_w, 1), device=canvas.device)

        # Aplicar opacidad global
        alpha = alpha * opacity

        # --- FUSIÓN (ALPHA BLENDING) ---
        # Coordenadas seguras (Clipping)
        y1, y2 = max(0, y_offset), min(H, y_offset + target_h)
        x1, x2 = max(0, x_offset), min(W, x_offset + target_w)

        # Coordenadas relativas al personaje (crop)
        cy1 = max(0, -y_offset)
        cy2 = cy1 + (y2 - y1)
        cx1 = max(0, -x_offset)
        cx2 = cx1 + (x2 - x1)

        if y2 > y1 and x2 > x1:
            # Región del fondo donde vamos a pintar
            bg_slice = canvas[:, y1:y2, x1:x2, :]
            # Región del personaje a pintar
            fg_slice = char_resized[:, cy1:cy2, cx1:cx2, :]
            # Región del alpha
            alpha_slice = alpha[cy1:cy2, cx1:cx2, :]

            # Fórmula: Pixel = (Foreground * Alpha) + (Background * (1 - Alpha))
            blended = (fg_slice * alpha_slice) + (bg_slice * (1.0 - alpha_slice))

            canvas[:, y1:y2, x1:x2, :] = blended

        # Crear máscara de salida para el Animator (solo la forma del personaje en el canvas)
        output_mask = torch.zeros((H, W), device=canvas.device)
        if y2 > y1 and x2 > x1:
             # Aquí ponemos 1s donde está el personaje
             output_mask[y1:y2, x1:x2] = alpha[cy1:cy2, cx1:cx2, 0]

        return (canvas, output_mask)

        # --- REGISTRO DEL NODO ---
        NODE_CLASS_MAPPINGS = {
            "SF_SceneComposer": SF_SceneComposer
        }
        NODE_DISPLAY_NAME_MAPPINGS = {
            "SF_SceneComposer": "🎬 SF Scene Composer"
        }