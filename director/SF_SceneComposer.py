import torch
import torch.nn.functional as F

class SF_SceneComposer:
    """
    Toma un personaje y un fondo, y los fusiona en coordenadas específicas.
    Genera automáticamente una máscara de atención para la animación.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "scene_image": ("IMAGE",),      # El fondo (Output del AssetLoader Escena)
                "character_image": ("IMAGE",),  # El personaje (Output del AssetLoader Personaje)
                "x_offset": ("INT", {"default": 0, "min": 0, "max": 4096, "step": 8}),
                "y_offset": ("INT", {"default": 0, "min": 0, "max": 4096, "step": 8}),
                "scale": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 5.0, "step": 0.1}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("composed_image", "fusion_mask")
    FUNCTION = "compose_scene"
    CATEGORY = "🧩 Studio Fury/🎬 Director"

    def compose_scene(self, scene_image, character_image, x_offset, y_offset, scale):
        # 1. Preparar el Lienzo (Scene)
        # ComfyUI usa formato [Batch, Height, Width, Channels]
        B, H, W, C = scene_image.shape
        canvas = scene_image.clone() # Creamos una copia para no destruir el original

        # 2. Procesar el Personaje
        # Necesitamos cambiar el formato para que Torch pueda redimensionar (permute)
        # De [B, H, W, C] a [B, C, H, W]
        char_tensor = character_image.permute(0, 3, 1, 2)

        # Calcular nuevas dimensiones
        char_h = int(character_image.shape[1] * scale)
        char_w = int(character_image.shape[2] * scale)

        # Redimensionar (Interpolación Bilineal para suavidad)
        char_resized = F.interpolate(char_tensor, size=(char_h, char_w), mode="bilinear", align_corners=False)

        # Devolver al formato Comfy [B, H, W, C]
        char_resized = char_resized.permute(0, 2, 3, 1)

        # 3. Composición (Pegar el personaje sobre el fondo)
        # Definir límites para no salirnos del cuadro
        y1 = max(0, y_offset)
        x1 = max(0, x_offset)
        y2 = min(H, y_offset + char_h)
        x2 = min(W, x_offset + char_w)

        # Calcular recortes si el personaje se sale del borde
        char_y1 = max(0, -y_offset)
        char_x1 = max(0, -x_offset)
        char_y2 = char_y1 + (y2 - y1)
        char_x2 = char_x1 + (x2 - x1)

        # Si las dimensiones son válidas, pegamos
        if y2 > y1 and x2 > x1:
            # Pegado simple (Reemplazo de píxeles)
            # NOTA: En la V2 implementaremos Alpha Blending si el personaje tiene transparencia
            canvas[:, y1:y2, x1:x2, :] = char_resized[:, char_y1:char_y2, char_x1:char_x2, :]

        # 4. Generación de Máscara (Fusion Mask)
        # Creamos una máscara negra del tamaño de la escena
        mask = torch.zeros((1, H, W), dtype=torch.float32)

        # Pintamos de blanco el área donde pusimos al personaje
        if y2 > y1 and x2 > x1:
            mask[:, y1:y2, x1:x2] = 1.0

        return (canvas, mask)

NODE_CLASS_MAPPINGS = {
    "SF_SceneComposer": SF_SceneComposer
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SF_SceneComposer": "🎨 SF Scene Composer"
}