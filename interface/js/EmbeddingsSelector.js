import { app } from "/scripts/app.js";

app.registerExtension({
    name: "StudioFury.EmbeddingsSelector",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "StudioFury_EmbeddingsSelector") {

            // --- CONFIGURACIÓN ---
            const ROW_HEIGHT = 22;
            const MAX_VISIBLE_ROWS = 10; // Aumentado a 10 para ver más
            const HEADER_HEIGHT = 70;
            const SCROLLBAR_WIDTH = 15;  // Más ancha para poder hacer clic

            const onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function() {
                const r = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

                this.emb_list = [];
                this.selection = {};
                this.scroll_offset = 0;

                // Calculamos altura fija
                const fixedHeight = HEADER_HEIGHT + (MAX_VISIBLE_ROWS * ROW_HEIGHT) + 20;
                this.setSize([360, fixedHeight]);

                // Ocultar inputs nativos
                if (this.widgets) {
                    for (const w of this.widgets) {
                        if (w.name === "embedding_list_raw") {
                            if (w.options && w.options.values) this.emb_list = w.options.values;
                            w.hidden = true;
                        }
                        if (w.name === "selected_data") w.hidden = true;
                    }
                }

                // --- EVENTO SCROLL (Definido en la instancia para prioridad) ---
                this.onMouseWheel = function(e) {
                    // Si el ratón está sobre el nodo, ejecutamos
                    if (!this.emb_list || this.emb_list.length <= MAX_VISIBLE_ROWS) return;

                    const delta = e.deltaY > 0 ? 1 : -1;
                    this.scroll_offset += delta;

                    // Límites
                    const max_offset = this.emb_list.length - MAX_VISIBLE_ROWS;
                    if (this.scroll_offset < 0) this.scroll_offset = 0;
                    if (this.scroll_offset > max_offset) this.scroll_offset = max_offset;

                    this.setDirtyCanvas(true, true);

                    // DETENER PROPAGACIÓN (Para que no haga zoom)
                    if(e.preventDefault) e.preventDefault();
                    if(e.stopPropagation) e.stopPropagation();
                    return true;
                };

                return r;
            };

            // --- BLOQUEO DE TAMAÑO ---
            nodeType.prototype.onResize = function(size) {
                const minHeight = HEADER_HEIGHT + (MAX_VISIBLE_ROWS * ROW_HEIGHT) + 20;
                size[0] = 360;
                size[1] = minHeight;
            };

            // --- DIBUJADO ---
            nodeType.prototype.onDrawForeground = function(ctx) {
                if (this.flags.collapsed) return;

                ctx.save();
                ctx.font = "12px Arial";

                // 1. Cabeceras
                let y_header = 50;
                ctx.fillStyle = "#aaa";
                ctx.fillText("Embedding File", 10, y_header);
                ctx.fillText("POS", 250, y_header);
                ctx.fillText("NEG", 300, y_header);

                ctx.strokeStyle = "#444";
                ctx.beginPath();
                ctx.moveTo(10, y_header + 8);
                ctx.lineTo(this.size[0] - 20, y_header + 8);
                ctx.stroke();

                const start_y = HEADER_HEIGHT;

                // 2. Lista
                if (this.emb_list && this.emb_list.length > 0) {
                    const visible_items = this.emb_list.slice(this.scroll_offset, this.scroll_offset + MAX_VISIBLE_ROWS);

                    for (let i = 0; i < visible_items.length; i++) {
                        const name = visible_items[i];
                        const row_y = start_y + (i * ROW_HEIGHT);

                        // Texto
                        ctx.fillStyle = "#ccc";
                        let displayName = name;
                        if(displayName.length > 28) displayName = displayName.substring(0, 25) + "...";
                        ctx.fillText(displayName, 10, row_y);

                        // Checkbox POS
                        const isPos = (this.selection[name] === 'P');
                        ctx.fillStyle = isPos ? "#0f0" : "#222";
                        ctx.fillRect(250, row_y - 10, 14, 14);
                        ctx.strokeStyle = "#666"; ctx.strokeRect(250, row_y - 10, 14, 14);

                        // Checkbox NEG
                        const isNeg = (this.selection[name] === 'N');
                        ctx.fillStyle = isNeg ? "#f00" : "#222";
                        ctx.fillRect(300, row_y - 10, 14, 14);
                        ctx.strokeStyle = "#666"; ctx.strokeRect(300, row_y - 10, 14, 14);
                    }

                    // 3. BARRA DE SCROLL + FLECHAS
                    if (this.emb_list.length > MAX_VISIBLE_ROWS) {
                        const total_height = MAX_VISIBLE_ROWS * ROW_HEIGHT;
                        const scroll_x = this.size[0] - SCROLLBAR_WIDTH - 5;

                        // Fondo barra
                        ctx.fillStyle = "#111";
                        ctx.fillRect(scroll_x, start_y - 10, SCROLLBAR_WIDTH, total_height);

                        // Thumb (Indicador)
                        const ratio = MAX_VISIBLE_ROWS / this.emb_list.length;
                        const thumb_height = (total_height - 30) * ratio; // -30 para dejar hueco a flechas
                        const scroll_track_h = total_height - 30;
                        const thumb_y = start_y + 5 + (this.scroll_offset / (this.emb_list.length - MAX_VISIBLE_ROWS)) * (scroll_track_h - thumb_height);

                        ctx.fillStyle = "#555";
                        ctx.roundRect(scroll_x + 2, thumb_y, SCROLLBAR_WIDTH - 4, thumb_height, 2);
                        ctx.fill();

                        // Flecha ARRIBA (▲)
                        ctx.fillStyle = "#888";
                        ctx.beginPath();
                        ctx.moveTo(scroll_x + SCROLLBAR_WIDTH/2, start_y - 8);
                        ctx.lineTo(scroll_x + 2, start_y + 2);
                        ctx.lineTo(scroll_x + SCROLLBAR_WIDTH - 2, start_y + 2);
                        ctx.fill();

                        // Flecha ABAJO (▼)
                        const bottom_y = start_y + total_height - 5;
                        ctx.beginPath();
                        ctx.moveTo(scroll_x + SCROLLBAR_WIDTH/2, bottom_y + 8);
                        ctx.lineTo(scroll_x + 2, bottom_y - 2);
                        ctx.lineTo(scroll_x + SCROLLBAR_WIDTH - 2, bottom_y - 2);
                        ctx.fill();
                    }
                } else {
                    ctx.fillStyle = "#666";
                    ctx.fillText("No embeddings found", 10, start_y);
                }
                ctx.restore();
            };

            // --- DETECCIÓN DE CLICS ---
            nodeType.prototype.onMouseDown = function(e, pos) {
                const x = pos[0];
                const y = pos[1];

                const start_y = HEADER_HEIGHT - 10;
                const list_height = MAX_VISIBLE_ROWS * ROW_HEIGHT;

                // 1. Clic en la LISTA (Checkboxes)
                if (y > start_y && y < start_y + list_height && x < this.size[0] - SCROLLBAR_WIDTH - 10) {
                    const visual_row_index = Math.floor((y - start_y) / ROW_HEIGHT);
                    const real_index = this.scroll_offset + visual_row_index;

                    if (this.emb_list && real_index >= 0 && real_index < this.emb_list.length) {
                        const name = this.emb_list[real_index];
                        if (x > 250 && x < 270) { // POS
                            this.selection[name] = (this.selection[name] === 'P') ? null : 'P';
                            this.updateOutput();
                            return true;
                        } else if (x > 300 && x < 320) { // NEG
                            this.selection[name] = (this.selection[name] === 'N') ? null : 'N';
                            this.updateOutput();
                            return true;
                        }
                    }
                }

                // 2. Clic en la BARRA DE SCROLL (Flechas)
                const scroll_x = this.size[0] - SCROLLBAR_WIDTH - 5;
                if (x > scroll_x && x < scroll_x + SCROLLBAR_WIDTH) {
                    // Flecha Arriba
                    if (y > start_y - 15 && y < start_y + 5) {
                        this.scroll_offset = Math.max(0, this.scroll_offset - 1);
                        this.setDirtyCanvas(true, true);
                        return true;
                    }
                    // Flecha Abajo
                    const bottom_y = start_y + list_height;
                    if (y > bottom_y - 15 && y < bottom_y + 15) {
                        const max_offset = this.emb_list.length - MAX_VISIBLE_ROWS;
                        this.scroll_offset = Math.min(max_offset, this.scroll_offset + 1);
                        this.setDirtyCanvas(true, true);
                        return true;
                    }
                }
            };

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