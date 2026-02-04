import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "ComfyUI-Studio-Fury.RefreshButton",
    setup(app) {
        // 1. Buscamos la barra de menú de ComfyUI
        const menu = document.querySelector(".comfy-menu");

        // Creamos un separador para que se vea ordenado
        const separator = document.createElement("hr");
        separator.style.margin = "5px 0";
        separator.style.borderColor = "#444";

        // 2. Creamos el botón estilo "Fury"
        const refreshBtn = document.createElement("button");
        refreshBtn.textContent = "🔄 Refresh Models (Fury)";
        refreshBtn.style.backgroundColor = "#722f37"; // Un rojo vino/oscuro (Estilo Fury)
        refreshBtn.style.color = "white";
        refreshBtn.style.fontWeight = "bold";
        refreshBtn.style.cursor = "pointer";
        refreshBtn.style.marginTop = "5px";
        refreshBtn.style.width = "100%"; // Que ocupe el ancho del menú

        // Efecto Hover simple
        refreshBtn.onmouseenter = () => refreshBtn.style.backgroundColor = "#a03b49";
        refreshBtn.onmouseleave = () => refreshBtn.style.backgroundColor = "#722f37";

        // 3. La lógica mágica
        refreshBtn.onclick = async () => {
             const originalText = refreshBtn.textContent;

             try {
                 refreshBtn.textContent = "⏳ Escaneando...";
                 refreshBtn.disabled = true;

                 // ESTA ES LA CLAVE: Llama a la función interna de Comfy que actualiza las listas
                 await app.refreshComboInNodes();

                 refreshBtn.textContent = "✅ ¡Listo!";
                 refreshBtn.style.backgroundColor = "#2d7d32"; // Verde éxito

                 // Volver al estado original después de 2 segundos
                 setTimeout(() => {
                     refreshBtn.textContent = originalText;
                     refreshBtn.disabled = false;
                     refreshBtn.style.backgroundColor = "#722f37";
                 }, 1500);

             } catch (e) {
                 console.error("Error al refrescar modelos:", e);
                 refreshBtn.textContent = "❌ Error";
                 refreshBtn.disabled = false;
             }
        };

        // 4. Insertamos el botón en el menú (normalmente al final)
        menu.append(separator);
        menu.append(refreshBtn);
    }
});