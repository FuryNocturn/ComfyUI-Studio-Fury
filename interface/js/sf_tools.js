import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

app.registerExtension({
    name: "StudioFury.Tools",

    async setup() {
        console.log("🧩 [StudioFury] Iniciando extensión de herramientas...");

        // Función para llamar a la API de Python
        const callApi = async (endpoint, confirmMsg) => {
            if (confirm(confirmMsg)) {
                try {
                    await api.fetchApi("/studiofury/system/" + endpoint, { method: "POST" });
                } catch (e) {
                    alert("Error conectando con Studio Fury: " + e);
                }
            }
        };

        // Función recursiva que espera a que la UI esté lista
        const addMenuItems = () => {
            // Comprobamos si el menú existe
            if (!app.ui || !app.ui.menu) {
                console.warn("⏳ [StudioFury] El menú aún no está listo. Reintentando en 1s...");
                setTimeout(addMenuItems, 1000); // Reintentar en 1 segundo
                return;
            }

            console.log("🧩 [StudioFury] Añadiendo botones al menú...");

            // 1. Botón REINICIAR
            app.ui.menu.addMenuItem({
                name: "SF-Restart",
                label: "🔄 SF: Reiniciar Servidor",
                callback: () => callApi("restart", "⚠️ ¿Reiniciar ComfyUI?\nLa conexión se perderá unos segundos.")
            });

            // 2. Botón APAGAR
            app.ui.menu.addMenuItem({
                name: "SF-Shutdown",
                label: "🛑 SF: Apagar Servidor",
                callback: () => callApi("shutdown", "🛑 ¿Apagar ComfyUI completamente?\nTendrás que abrir la consola manualmente.")
            });

            console.log("✅ [StudioFury] Botones añadidos correctamente.");
        };

        // Iniciamos el intento de añadir botones
        addMenuItems();
    }
});