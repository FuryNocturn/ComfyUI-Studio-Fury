# 🧩 Studio Fury (v2.0.0)

![Python Version](https://img.shields.io/badge/python-3.12%2B-blue)
![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom_Node-green)
![License](https://img.shields.io/github/license/FuryNocturn/ComfyUI-Studio-Fury)
![Version](https://img.shields.io/badge/version-2.0.1-orange)

### Pro AI Art Direction & Advanced Workflows for ComfyUI

**Studio Fury** es una suite profesional de nodos diseñados para transformar ComfyUI en una estación de trabajo de dirección de arte integral. Optimiza la gestión de personajes, escenas y activos mediante una arquitectura de **Bus de Datos (SF_LINK)**, permitiendo flujos de trabajo escalables y organizados.

---

## 🚀 Características Principales

* **Bus de Datos Inteligente (Charged Bus):** Olvídate del "espagueti de cables". El sistema `SF_LINK` empaqueta modelos, CLIP, VAE y entidades en un solo flujo.
* **Selector Visual de Embeddings:** Interfaz personalizada para gestionar tus embeddings con un solo clic (Positivo/Negativo/Neutral) directamente en el nodo.
* **Gestión de Proyectos Real:** Sistema de archivos estructurado que organiza automáticamente personajes, escenas y renders en tu carpeta de `output`.
* **Director Engine:** Motor dinámico para generar entidades (personajes y fondos) de forma masiva con limpieza automática de memoria GPU.
* **Scene Composer:** Sistema de composición de alta fidelidad con blending de tensores en GPU y control de opacidad/escala.
* **Action Animator:** Preparación de batches latentes con restricciones de movimiento (Motion Freedom) para flujos de video estables.

---

## 📦 Instalación

### Opción 1: ComfyUI Manager (Recomendado)
* Busca `Studio Fury` en la base de datos del Manager e instálalo directamente.

### Opción 2: Instalación Manual
1.  Navega a tu carpeta de nodos personalizados:
    ```bash
    cd ComfyUI/custom_nodes/
    ```
2.  Clona el repositorio:
    ```bash
    git clone [https://github.com/FuryNocturn/ComfyUI-Studio-Fury.git](https://github.com/FuryNocturn/ComfyUI-Studio-Fury.git)
    ```
3.  Instala las dependencias necesarias:
    ```bash
    pip install -r requirements.txt
    ```

---

## 🛠️ Nodos Incluidos

### 📦 Dataset & Project
- **Project Manager:** Inicializa tu proyecto y define el VAE/CLIP base.
- **Add Entity:** Registra personajes o escenas con prompts específicos y configuraciones de Aspect Ratio.
- **Smart Saver:** Guarda tus activos en formato técnico `.fury` (tensores serializados) y previsualización `.png`.

### 📝 Prompts
- **Advanced Prompt:** Constructor de prompts profesional dividido por: Calidad, Estilo, Cámara, Sujeto y Entorno.
- **Embeddings Selector:** El gestor visual definitivo para tus archivos de embeddings.

### 🎬 Director & Render
- **Director Engine:** El cerebro del renderizado masivo.
- **Fury Sampler:** Sampler optimizado con integración directa al bus de datos.
- **Scene Composer:** Montaje de personajes sobre fondos con control espacial.
- **Action Animator:** Generador de latentes para animación con máscara de restricción de ruido.

---

## ⚙️ Control de Sistema
Studio Fury añade herramientas administrativas al menú superior de ComfyUI:
* **🔄 Restart Server:** Reinicia el servidor de ComfyUI sin cerrar la terminal.
* **🛑 Shutdown Server:** Apaga completamente la instancia de ComfyUI de forma segura.

---

## 🤝 Contribuciones
¡Las contribuciones son bienvenidas! Si tienes ideas para nuevos nodos basados en el sistema de Bus o mejoras en la interfaz JS, no dudes en abrir un *Issue* o enviar un *Pull Request*.

**Autor:** [FuryNocturn](https://github.com/FuryNocturn)  
**Licencia:** MIT  
**Versión:** 2.0.0
