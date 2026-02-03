import { app } from "../../scripts/app.js";

app.registerExtension({
    name: "StudioFury.PowerButton",
    setup(app) {
        // Buscamos la barra de menú (donde están los botones de Queue, etc.)
        const menu = document.querySelector(".comfy-menu");

        if (menu) {
            // Creamos el separador visual
            const separator = document.createElement("hr");
            separator.style.margin = "10px 0";
            separator.style.borderColor = "#444";
            menu.appendChild(separator);

            // Creamos el botón de APAGADO
            const powerBtn = document.createElement("button");
            powerBtn.textContent = "🛑 APAGAR SISTEMA";

            // Estilos para que parezca peligroso/importante
            powerBtn.style.backgroundColor = "#500"; // Rojo oscuro
            powerBtn.style.color = "white";
            powerBtn.style.fontWeight = "bold";
            powerBtn.style.marginTop = "5px";
            powerBtn.style.cursor = "pointer";
            powerBtn.style.border = "1px solid #f00";

            // Efecto Hover
            powerBtn.onmouseenter = () => { powerBtn.style.backgroundColor = "#f00"; };
            powerBtn.onmouseleave = () => { powerBtn.style.backgroundColor = "#500"; };

            // La Lógica al hacer Click
            powerBtn.onclick = async () => {
                const confirmacion = confirm("⚠️ ¿Estás seguro?\n\nEsto cerrará el proceso de Python y detendrá ComfyUI completamente.");

                if (confirmacion) {
                    try {
                        // Cambiamos el texto para feedback visual
                        powerBtn.textContent = "APAGANDO...";
                        powerBtn.disabled = true;

                        // Llamamos a nuestra API en Python
                        await fetch('/studiofury/system/shutdown', {
                            method: 'POST'
                        });

                        // Intentamos cerrar la pestaña (los navegadores a veces bloquean esto)
                        window.close();

                        // Si no se cierra, mostramos mensaje final
                        document.body.innerHTML = `
                            <div style="display:flex; justify-content:center; align-items:center; height:100vh; background:#111; color:#f00; font-family:sans-serif; flex-direction:column;">
                                <h1 style="font-size:50px;">SISTEMA APAGADO</h1>
                                <p>Ya puedes cerrar esta pestaña.</p>
                            </div>
                        `;

                    } catch (error) {
                        // Como el servidor muere, el fetch dará error de red, lo cual es BUENO en este caso.
                        // Así que asumimos éxito si falla la conexión después de llamar.
                        document.body.innerHTML = "<h1 style='color:white; text-align:center; margin-top:20%'>🛑 Conexión Terminada.</h1>";
                    }
                }
            };

            // Añadimos el botón al menú
            menu.appendChild(powerBtn);
        }
    }
});