import { app } from "/scripts/app.js";

app.registerExtension({
    name: "StudioFury.EmbeddingsSelector",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "StudioFury_EmbeddingsSelector") {

            // CONFIGURACIÓN VISUAL
            const ROW_HEIGHT = 25;       // Altura de cada fila
            const MAX_VISIBLE_ROWS = 5;  // Cuántas filas ver a la vez
            const HEADER_HEIGHT = 80;    // Espacio reservado arriba (para no tapar outputs)
            const SCROLLBAR_WIDTH = 10;

            const onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function() {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

                this.emb_list = [];
                this.selection = {};
                this.scroll_offset = 0; // Posición inicial del scroll

                // Tamaño fijo calculado: Cabecera + (Filas * Altura) + Margen
                const fixedHeight = HEADER_HEIGHT + (MAX_VISIBLE_ROWS * ROW_HEIGHT) + 10;
                this.setSize([350, fixedHeight]);

                // Ocultar widgets nativos
                if (this.widgets) {
                    for (const w of this.widgets) {
                        if (w.name === "embedding_list_raw") {
                            if (w.options && w.options.values) this.emb_list = w.options.values;
                            w.hidden = true;
                        }
                        if (w.name === "selected_data") w.hidden = true;
                    }
                }
                return r;
            };

            // 1. EVENTO DE RUEDA DE RATÓN (SCROLL)
            nodeType.prototype.onMouseWheel = function(e) {
                if (!this.emb_list || this.emb_list.length <= MAX_VISIBLE_ROWS) return;

                // Detectar dirección
                const delta = e.deltaY > 0 ? 1 : -1;
                this.scroll_offset += delta;

                // Limitar scroll (Clamping)
                const max_offset = this.emb_list.length - MAX_VISIBLE_ROWS;
                if (this.scroll_offset < 0) this.scroll_offset = 0;
                if (this.scroll_offset > max_offset) this.scroll_offset = max_offset;

                // Redibujar
                this.setDirtyCanvas(true, true);
            };

            // 2. RESTRICCIÓN DE TAMAÑO (Para que no lo hagan pequeño)
            nodeType.prototype.onResize = function(size) {
                const minHeight = HEADER_HEIGHT + (MAX_VISIBLE_ROWS * ROW_HEIGHT) + 10;
                if (size[0] < 350) size[0] = 350;
                if (size[1] < minHeight) size[1] = minHeight;
            };

            // 3. DIBUJADO (ON DRAW)
            nodeType.prototype.onDrawForeground = function(ctx) {
                if (this.flags.collapsed) return;

                ctx.save();
                ctx.font = "12px Arial";

                // A. DIBUJAR CABECERAS (Bajadas a Y=60 para no tapar outputs)
                let y_header = 60;

                ctx.fillStyle = "#aaa";
                ctx.fillText("Embedding File", 10, y_header);
                ctx.fillText("POS", 240, y_header);
                ctx.fillText("NEG", 290, y_header);

                // Línea separadora
                ctx.strokeStyle = "#444";
                ctx.beginPath();
                ctx.moveTo(10, y_header + 8);
                ctx.lineTo(this.size[0] - 20, y_header + 8);
                ctx.stroke();

                // B. DIBUJAR LISTA (Solo la parte visible)
                const start_y = HEADER_HEIGHT;

                if (this.emb_list && this.emb_list.length > 0) {

                    // Definir rango visible
                    const visible_items = this.emb_list.slice(this.scroll_offset, this.scroll_offset + MAX_VISIBLE_ROWS);

                    for (let i = 0; i < visible_items.length; i++) {
                        const item_index = this.scroll_offset + i; // Índice real en la lista completa
                        const name = visible_items[i];
                        const row_y = start_y + (i * ROW_HEIGHT);

                        // Texto (cortado si es muy largo)
                        ctx.fillStyle = "#ccc";
                        let displayName = name;
                        if(displayName.length > 25) displayName = displayName.substring(0, 22) + "...";
                        ctx.fillText(displayName, 10, row_y);

                        // Checkbox POS
                        const isPos = (this.selection[name] === 'P');
                        ctx.fillStyle = isPos ? "#0f0" : "#222";
                        ctx.fillRect(240, row_y - 10, 14, 14);
                        ctx.strokeStyle = "#888"; ctx.strokeRect(240, row_y - 10, 14, 14);

                        // Checkbox NEG
                        const isNeg = (this.selection[name] === 'N');
                        ctx.fillStyle = isNeg ? "#f00" : "#222";
                        ctx.fillRect(290, row_y - 10, 14, 14);
                        ctx.strokeStyle = "#888"; ctx.strokeRect(290, row_y - 10, 14, 14);
                    }

                    // C. DIBUJAR BARRA DE SCROLL (Si hace falta)
                    if (this.emb_list.length > MAX_VISIBLE_ROWS) {
                        const total_height = MAX_VISIBLE_ROWS * ROW_HEIGHT;
                        const scroll_x = this.size[0] - SCROLLBAR_WIDTH - 5;

                        // Fondo de la barra
                        ctx.fillStyle = "#111";
                        ctx.fillRect(scroll_x, start_y - 15, SCROLLBAR_WIDTH, total_height);

                        // El "Thumb" (la parte que se mueve)
                        const ratio = MAX_VISIBLE_ROWS / this.emb_list.length;
                        const thumb_height = total_height * ratio;
                        const thumb_y = start_y - 15 + (this.scroll_offset / this.emb_list.length) * total_height;

                        ctx.fillStyle = "#666";
                        ctx.fillRect(scroll_x, thumb_y, SCROLLBAR_WIDTH, thumb_height);
                    }
                } else {
                    ctx.fillStyle = "#666";
                    ctx.fillText("No embeddings found", 10, start_y);
                }

                ctx.restore();
            };

            // 4. DETECCIÓN DE CLICS (INTERACCIÓN)
            nodeType.prototype.onMouseDown = function(e, pos) {
                const x = pos[0];
                const y = pos[1];

                const start_y = HEADER_HEIGHT - 15; // Ajuste fino para coincidir con el dibujo
                const list_height = MAX_VISIBLE_ROWS * ROW_HEIGHT;

                // Si el clic está fuera del área de lista, ignorar
                if (y < start_y || y > start_y + list_height) return;

                // Calcular en qué fila visual hizo clic (0 a 4)
                const visual_row_index = Math.floor((y - start_y) / ROW_HEIGHT);

                // Calcular el índice real en el array
                const real_index = this.scroll_offset + visual_row_index;

                if (this.emb_list && real_index >= 0 && real_index < this.emb_list.length) {
                    const name = this.emb_list[real_index];

                    // Columna POS
                    if (x > 240 && x < 260) {
                        this.selection[name] = (this.selection[name] === 'P') ? null : 'P';
                        this.updateOutput();
                        return true;
                    }
                    // Columna NEG
                    else if (x > 290 && x < 310) {
                        this.selection[name] = (this.selection[name] === 'N') ? null : 'N';
                        this.updateOutput();
                        return true;
                    }
                }
            };

            // Actualizar widget oculto
            nodeType.prototype.updateOutput = function() {
                let out = [];
                for(let k in this.selection) {
                    if(this.selection[k]) out.push(this.selection[k] + ":" + k);
                }
                const w = this.widgets.find(w => w.name === "selected_data");
                if(w) w.value = out.join("|");
            };
        }
    }
});