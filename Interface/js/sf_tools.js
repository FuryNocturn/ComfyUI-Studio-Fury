import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

// =============================================================================
// 1. LOS DIBUJOS (SVGS)
// Sin esto, la nueva interfaz no sabe qué pintar y no muestra el botón.
// =============================================================================

// Icono: Carita Feliz (Para el botón Hola)
const ICON_HOLA = `
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2">
  <circle cx="12" cy="12" r="10" />
  <path d="M8 14s1.5 2 4 2 4-2 4-2" />
  <line x1="9" y1="9" x2="9.01" y2="9" />
  <line x1="15" y1="9" x2="15.01" y2="9" />
</svg>`;

// Icono: Power (Para el botón Apagar)
const ICON_POWER = `
<svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="red" stroke-width="2">
  <path d="M18.36 6.64a9 9 0 1 1-12.73 0" />
  <line x1="12" y1="2" x2="12" y2="12" />
</svg>`;

// =============================================================================
// 2. LAS ACCIONES
// =============================================================================

const actionHola = () => {
    alert("👋 ¡HOLA! El sistema de botones funciona.");
};

const actionShutdown = async () => {
    if (confirm("⚠️ ¿APAGAR STUDIO FURY?")) {
        try {
            await api.fetchApi('/studiofury/system/shutdown', { method: 'POST' });
            document.body.innerHTML = "<h1 style='color:red;text-align:center;margin-top:20%'>🛑 APAGADO</h1>";
            document.body.style.background = "black";
            window.close();
        } catch (e) { console.error(e); }
    }
};

// =============================================================================
// 3. REGISTRO OFICIAL (CLONANDO LORA MANAGER)
// =============================================================================

app.registerExtension({
    name: "StudioFury.Buttons",

    // Le pedimos sitio en la barra
    actionBarButtons: [
        {
            id: "sf-hello",
            icon: "sf-placeholder", // Nombre temporal
            tooltip: "Probar Botón Hola",
            onClick: actionHola
        },
        {
            id: "sf-kill",
            icon: "sf-placeholder",
            tooltip: "Apagar Sistema",
            onClick: actionShutdown
        }
    ],

    async setup() {
        console.log("🧩 [StudioFury] Iniciando inyección de iconos SVG...");

        // Función que busca los botones y les mete el dibujo SVG dentro
        const injectIcons = () => {
            // Buscamos por el texto de ayuda (Tooltip)
            const btnHola = document.querySelector('button[title="Probar Botón Hola"]');
            const btnKill = document.querySelector('button[title="Apagar Sistema"]');

            // Si no están, reintentamos en el siguiente frame
            if (!btnHola || !btnKill) {
                requestAnimationFrame(injectIcons);
                return;
            }

            // --- INYECCIÓN DEL ICONO HOLA ---
            // Limpiamos lo que tenga y metemos nuestro SVG
            btnHola.innerHTML = ICON_HOLA;
            Object.assign(btnHola.style, {
                color: "#88ff88", // Verde
                padding: "4px"
            });

            // --- INYECCIÓN DEL ICONO POWER ---
            btnKill.innerHTML = ICON_POWER;
            Object.assign(btnKill.style, {
                color: "#ff8888", // Rojo
                padding: "4px",
                marginLeft: "5px",
                borderLeft: "1px solid #444" // Separador visual
            });
        };

        // Arrancar el bucle de búsqueda
        requestAnimationFrame(injectIcons);
    }
});