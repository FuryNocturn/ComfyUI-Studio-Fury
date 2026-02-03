import folder_paths
import locale

# --- CORRECCIÓN: Definimos la función directamente ---
def get_lang_text(en, es):
    try:
        sys_lang = locale.getdefaultlocale()[0]
        is_spanish = sys_lang and "es" in sys_lang.lower()
    except:
        is_spanish = False
    return es if is_spanish else en

class StudioFury_EmbeddingsSelector:
    @classmethod
    def INPUT_TYPES(s):
        file_list = folder_paths.get_filename_list("embeddings")
        file_list.sort()

        return {
            "required": {
                "selected_data": ("STRING", {"default": "", "multiline": False, "hidden": True}),
            },
            "optional": {
                "embedding_list_raw": (file_list, ),
            }
        }

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = (get_lang_text("Positive Text", "Texto Positivo"), get_lang_text("Negative Text", "Texto Negativo"))
    FUNCTION = "process"
    CATEGORY = "🧩 Studio Fury/📝 Prompts"

    def process(self, selected_data, embedding_list_raw=None):
        pos_stack = []
        neg_stack = []

        if selected_data:
            items = selected_data.split("|")
            for item in items:
                if item.startswith("P:"):
                    pos_stack.append(f"embedding:{item[2:]}")
                elif item.startswith("N:"):
                    neg_stack.append(f"embedding:{item[2:]}")

        return (", ".join(pos_stack), ", ".join(neg_stack))

NODE_CLASS_MAPPINGS = {
    "StudioFury_EmbeddingsSelector": StudioFury_EmbeddingsSelector
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "StudioFury_EmbeddingsSelector": get_lang_text("Embeddings List 💉", "Lista Embeddings 💉")
}