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
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "fury_bus": ("SF_LINK",),
                "clip": ("CLIP",),
                # Negativo Global: Solo cosas técnicas de imagen, NO anatomía ni contenido.
                "global_negative": ("STRING", {"default": "low quality, blurry, jpeg artifacts, watermark, text, signature", "multiline": True}),
            },
            "optional": {
                # PROTAGONISTA 1
                "P1_Positive": ("STRING", {"multiline": True, "default": "detailed character description..."}),
                "P1_Negative": ("STRING", {"multiline": True, "default": ""}), # Específico (ej: "hat, glasses")

                # PROTAGONISTA 2
                "P2_Positive": ("STRING", {"multiline": True, "default": ""}),
                "P2_Negative": ("STRING", {"multiline": True, "default": ""}),

                # ESCENA 1
                "S1_Positive": ("STRING", {"multiline": True, "default": "beautiful scenery..."}),
                "S1_Negative": ("STRING", {"multiline": True, "default": ""}), # Específico (ej: "cars, animals")

                # ESCENA 2
                "S2_Positive": ("STRING", {"multiline": True, "default": ""}),
                "S2_Negative": ("STRING", {"multiline": True, "default": ""}),
            }
        }

    RETURN_TYPES = ("SF_LINK",)
    RETURN_NAMES = ("charged_bus",)
    FUNCTION = "process_prompts"
    CATEGORY = "🧩 Studio Fury/📦 Dataset"

    def process_prompts(self, fury_bus, clip, global_negative, **kwargs):
        bus = fury_bus.copy()

        # Función auxiliar para codificar texto a condicionamiento
        def encode(text):
            tokens = clip.tokenize(text)
            cond, pooled = clip.encode_from_tokens(tokens, return_pooled=True)
            return [[cond, {"pooled_output": pooled}]]

        # Mapeo de inputs a las claves del bus
        # (ClaveEntidad : (CampoPositivo, CampoNegativo))
        input_map = {
            "P1": ("P1_Positive", "P1_Negative"),
            "P2": ("P2_Positive", "P2_Negative"),
            "S1": ("S1_Positive", "S1_Negative"),
            "S2": ("S2_Positive", "S2_Negative")
        }

        # --- LÓGICA DE INYECCIÓN AUTOMÁTICA ---
        auto_neg_character = "bad anatomy, missing limbs, extra fingers, bad hands, mutated, deformed, amputation"
        auto_neg_scene = "people, crowd, pedestrians, humans, person, man, woman, character, faces"

        print(f"⚡ [PromptEngine] Procesando prompts inteligentes...")

        for key, data in bus["entities"].items():
            # Identificamos qué campos leer
            fields = input_map.get(key)
            if not fields: continue

            user_pos = kwargs.get(fields[0], "")
            user_neg = kwargs.get(fields[1], "")

            # 1. Construcción del Prompt POSITIVO
            if not user_pos.strip():
                user_pos = f"high quality {data['type']} of {data['name']}"

            # 2. Construcción del Prompt NEGATIVO (En capas)
            # Capa 1: Global (Calidad)
            final_neg = global_negative

            # Capa 2: Específico del Usuario (Si escribió algo)
            if user_neg.strip():
                final_neg += f", {user_neg}"

            # Capa 3: Automática por TIPO (Aquí está la magia)
            if data["type"] == "character":
                final_neg += f", {auto_neg_character}"
            elif data["type"] == "scene":
                final_neg += f", {auto_neg_scene}"

            # Debug para que veas qué está haciendo
            print(f"   🔹 {data['name']} ({data['type']}):")
            print(f"      [+] {user_pos[:30]}...")
            print(f"      [-] ...{final_neg[-50:]}")

            # Codificamos y guardamos en el bus
            data["cond_pos"] = encode(user_pos)
            data["cond_neg"] = encode(final_neg)

        return (bus,)

NODE_CLASS_MAPPINGS = { "SF_FuryPromptEngine": SF_FuryPromptEngine }
NODE_DISPLAY_NAME_MAPPINGS = { "SF_FuryPromptEngine": "2️⃣ SF Prompt Engine (Smart Layers)" }