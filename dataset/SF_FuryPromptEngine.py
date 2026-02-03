import torch
import os
import sys

# --- FIX IMPORT ---
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
project_root = os.path.dirname(current_dir)
if project_root not in sys.path: sys.path.append(project_root)
# ------------------

class SF_FuryPromptEngine:
    """
    Recibe el Bus y permite escribir prompts específicos para cada entidad detectada.
    Inyecta el Conditioning (Tensores) dentro del Bus.
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "fury_bus": ("SF_LINK",),
                "clip": ("CLIP",),
                # Definimos campos genéricos. En el futuro con JS pueden ser dinámicos.
                # Por ahora, el usuario debe rellenar los que coincidan con su Manager.
            },
            "optional": {
                "P1_Positive": ("STRING", {"multiline": True, "default": "Protag 1 details..."}),
                "P1_Negative": ("STRING", {"multiline": True, "default": "bad quality..."}),
                "P2_Positive": ("STRING", {"multiline": True, "default": "Protag 2 details..."}),
                "P2_Negative": ("STRING", {"multiline": True, "default": "bad quality..."}),
                "S1_Positive": ("STRING", {"multiline": True, "default": "Scene 1 details..."}),
                "S1_Negative": ("STRING", {"multiline": True, "default": "bad quality..."}),
                # Se pueden añadir más si se necesitan
            }
        }

    RETURN_TYPES = ("SF_LINK",)
    RETURN_NAMES = ("charged_bus",)
    FUNCTION = "process_prompts"
    CATEGORY = "🧩 Studio Fury/📦 Dataset"

    def process_prompts(self, fury_bus, clip, **kwargs):
        # Clonamos el bus para no alterar el original inadvertidamente
        bus = fury_bus.copy()

        # Función auxiliar para codificar
        def get_conditioning(text):
            tokens = clip.tokenize(text)
            cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)
            return [[cond, {"pooled_output": pooled}]]

        # Mapeo manual de entradas a entidades (Limitación visual de ComfyUI sin JS avanzado)
        # P1 -> protag_1, S1 -> scene_1, etc.
        mapping = {
            "protag_1": ("P1_Positive", "P1_Negative"),
            "protag_2": ("P2_Positive", "P2_Negative"),
            "scene_1":  ("S1_Positive", "S1_Negative"),
            "scene_2":  ("S2_Positive", "S2_Negative"),
        }

        # Procesamiento
        for entity_key, config in bus["entities"].items():
            if entity_key in mapping:
                pos_field, neg_field = mapping[entity_key]

                # Obtener texto de los inputs opcionales
                pos_text = kwargs.get(pos_field, "")
                neg_text = kwargs.get(neg_field, "")

                # Si hay texto, codificamos y guardamos en el BUS
                if pos_text:
                    print(f"⚡ [FuryPrompt] Codificando para {config['name']}...")
                    config["prompts"]["positive"] = get_conditioning(pos_text)
                    config["prompts"]["negative"] = get_conditioning(neg_text)
                    config["prompts"]["raw_pos"] = pos_text # Guardamos texto crudo por si acaso

        return (bus,)

NODE_CLASS_MAPPINGS = { "SF_FuryPromptEngine": SF_FuryPromptEngine }
NODE_DISPLAY_NAME_MAPPINGS = { "SF_FuryPromptEngine": "📝 Fury Prompt Engine" }