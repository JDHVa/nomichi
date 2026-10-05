# TerraOrbis / HarvestMind — nomichi

Robot terrestre autónomo que patrulla cultivos y detecta plagas, enfermedades y hongos por visión artificial. Proyecto STEM 2025, UANL — Escuela Industrial y Preparatoria Técnica "Álvaro Obregón", Mecatrónica Industrial Bilingüe Progresivo Alemán (Monterrey, N.L.).

## Reglas de trabajo (obligatorias)

- **No poner comentarios en el código ni en los archivos.** Nada de `#` explicativos ni docstrings decorativos. Toda explicación va en este archivo (GEMINI.md) o en CLAUDE.md.
- **Ejecutar todo dentro del `venv`** del proyecto: `./venv/Scripts/python.exe ...`
- La API key de Roboflow va en `.env` (no versionado). La key anterior quedó expuesta: **regenerarla** en Roboflow.
- `venv/`, `.env` y `datasets/` están en `.gitignore` y no se suben.

## Rol de Gemini en el proyecto

- **Deep Research:** buscar datasets, documentar ciclos de vida de plagas y el marco teórico, redactar/mejorar el reporte. NO corre en el robot.
- **Gemini Vision (nube):** opcional, como "segunda opinión" para detecciones de baja confianza cuando hay internet.
- **El detector del robot NO es Gemini:** es YOLOv8 sobre el acelerador Hailo, offline y en tiempo real.

## Decisiones de arquitectura de IA

- **Detector: YOLOv8s (detección de objetos) compilado a formato Hailo HEF.** Alternativa: YOLO11s.
- **Se descarta FOMO** (era para microcontroladores; solo da centroides). Se actualiza el YOLOv5 del reporte original.
- **Acelerador: AI HAT+ con Hailo-8 (26 TOPS)** sobre Raspberry Pi 5. Con 26 TOPS corre YOLOv8s/m holgado; bajar a `n` si se necesita más FPS.
- **Pipeline:** entrenar con Ultralytics (PC/Colab) → exportar ONNX → compilar a HEF con Hailo Dataflow Compiler (cuantización INT8) → desplegar en Pi 5 con HailoRT + `hailo-rpi5-examples` o DeGirum PySDK.

## Fase 1 (actual): datasets

Objetivo: juntar datasets públicos y armar el pipeline de datos.

- **Cultivos prioritarios: chile + tomate** (mejor cobertura de datos, comparten plagas). Sandía, tomatillo fresadilla y melón se agregan después.
- **Datos: datasets públicos ahora; fotos reales de campo (Linares) más adelante** para fine-tuning.

### Datasets descargados (en `datasets/`, formato yolov8)

- `datasets/plantdoc` — multicultivo campo (in-the-wild), `joseph-nelson/plantdoc` v4. 30 clases; útiles: 9 de tomate (Early blight, Septoria, bacterial spot, late blight, mosaic virus, yellow virus, mold, spider mites, leaf) + Bell_pepper (leaf, leaf spot). ~2009/314/246. **Fundación de campo** recomendada.
- `datasets/tom` — tomate, `bryan-b56jm/tomato-leaf-disease-ssoha` v63. 9 clases (Early/Late Blight, Leaf Miner, Leaf Mold, Mosaic, Septoria, Spider Mites, Healthy). ~9039/843/165. Volumen alto pero **calidad mixta** (parece scraping/auto-etiquetado; contiene hasta una foto de papa). No depender solo de él.
- `datasets/chili_plant_disease` — chile, `ml-vpzcc/chili-plant-disease` v3. 5 clases: healthy, leaf curl, leaf spot, whitefly, yellow. ~335/46/47.
- `datasets/pests_aphid_thrips_whitefly` — plagas, `samm-v6vxt/pests-wwm0o` v3. 3 clases: Aphids, Thrips, Whiteflies. ~1493/442/213.
- `datasets/tomato_village` — tomate **campo real** (Rajasthan), 8 clases (con cajas: Late Blight, Leaf Miner, Mg/N/K Deficiency, Spotted Wilt Virus; Early_blight y Healthy sin cajas). ~11493 train / 2875 val imgs, 161k cajas. **Único con deficiencias nutricionales + spotted wilt virus.** `data.yaml` en `datasets/tomato_village/data.yaml`; imágenes en `Variant-c(Object Detection)/{train,val}/images`, labels en `.../labels`. Desbalance fuerte (Leaf Miner ~107k cajas) → usar class weights / undersampling.
- `datasets/plantdoc_tomatoes` — tomate campo, `tomatoes/plantdoc-tomatoes` v28. Solo 2 clases (Healthy/Unhealthy) → débil, referencia.
- Peso total actual: ~2.8 GB.

Reproducir Tomato-Village (el mirror de Kaggle trae **labels Y ~90% de imágenes corruptas** con "429: Too Many Requests"): usar el repo oficial `github.com/mamta-joshi-gehlot/Tomato-Village` como fuente real. Sparse-checkout (blob:none) de `Variant-c(Object Detection)/{train,val}/{yolo,images}` y reemplazar imágenes+labels en `datasets/tomato_village`. `scripts/preparar_tomato_village.py` empareja, normaliza el id de clase (`3.0`→`3`) y escribe el `data.yaml`. `scripts/unificar_tomate.py` además valida cada imagen con PIL y salta cualquier corrupta.

### Notas de datos (del análisis en "Datasets de Enfermedades en Tomate.docx")

- **NO mezclar PlantVillage** (laboratorio) con datasets de campo: causa data leakage y domain shift (95% mAP en train, falla en campo). Muchos "Tomato Disease YOLOv8" de Kaggle son PlantVillage auto-etiquetado → evitar.
- Estrategia recomendada: fundación de campo (PlantDoc + Tomato-Village) → refinar → (avanzado) copy-paste de lesiones de PlantVillage sobre fondos reales. Evaluar con mAP@0.5:0.95, no solo mAP@0.5.
- Candidatos por agregar: **Tomato-Village** (Kaggle, campo, alto valor), **DiaMOS** (Zenodo, CC BY 4.0), **Mendeley viral/moho gris/marchitez** (fine-tuning). PlantSeg (segmentación, acceso restringido).

### Nota Windows (rutas largas)

Windows limita rutas a 260 caracteres y no hay admin para activar LongPathsEnabled. Datasets con nombres de archivo larguísimos (PlantDoc, tomate) se extraen con `scripts/extraer_zip_largo.py` (prefijo `\\?\`). `scripts/descargar_datasets.py` ya hace este fallback automático.

### Pasos

1. Descargar datasets → `scripts/descargar_datasets.py` (los guarda en `datasets/`).
2. Definir taxonomía unificada de clases → `datasets/clases.yaml`.
3. Fusionar y estandarizar a YOLOv8 con split 70/20/10 → `scripts/unificar_dataset.py`.
4. Verificar peso, conteo por clase e inspección visual de cajas.

## Arquitectura de modelos: UN modelo por cultivo

Decisión: **un modelo de detección por cultivo** (no un modelo por enfermedad, ni un solo mega-modelo). El robot patrulla un cultivo a la vez y carga el modelo correspondiente → corre 1 solo modelo en el Hailo a máxima velocidad. Las **plagas (mosca blanca, pulgón, trips) se incluyen DENTRO de cada modelo de cultivo** (no un modelo de plagas aparte). Secuencia: **Tomate primero** (hay datos), **Chile después** (falta reforzar datos). Se puede fusionar en un solo modelo el día que haya datos parejos.

## Modelo Tomate: dataset unificado (`datasets/tomato_model`)

Construido con `scripts/unificar_tomate.py` (mapea las clases de cada fuente a una taxonomía canónica, descarta pimiento/otros cultivos, usa hardlinks para no duplicar disco) y auditado con `scripts/auditar.py`.

- Fuentes: `tom` + subconjunto de tomate de `plantdoc` + `tomato_village` + `pests_aphid_thrips_whitefly`. Excluido `plantdoc_tomatoes` (Healthy/Unhealthy muy burdo).
- 17 clases: tomato_healthy, early_blight, late_blight, septoria, leaf_mold, mosaic_virus, yellow_leaf_curl_virus, bacterial_spot, spider_mites, leaf_miner, spotted_wilt_virus, magnesium/nitrogen/potassium_deficiency, whitefly, aphid, thrips.
- Splits: 21586 train / 4334 val / 1382 test. Auditoría: 0 huérfanos, 0 fugas, 0 problemas de etiqueta, 237,802 cajas.
- **Split group-aware (importante):** se ignoran los splits originales de cada fuente y se reparte POR IMAGEN ORIGINAL (todas las aumentaciones de una foto van al mismo split), con hash determinista sobre `fuente/base`. Esto evita fuga de datos. Motivo: `tomato_village` traía el 100% de sus bases de val también en train, y `pests` ~88% (fuga severa); `tom` ~9%; `plantdoc` limpio. `base_original()` en `unificar_tomate.py` normaliza nombres de roboflow (`_jpg.rf.<hash>`) y de village (`_augN`).
- Ojo diversidad: `tomato_village` son ~1796 fotos originales (todas del mismo día) muy aumentadas → poca variedad real; sus clases (deficiencias, spotted wilt) pueden no generalizar a otras condiciones hasta sumar fotos propias.
- Desbalance fuerte: leaf_miner 46.5%, spotted_wilt 13.2%, aphid 10.6%; escasas bacterial_spot 0.2%, potassium_def 0.5%, nitrogen_def 0.7% → usar class weights / augmentation al entrenar.
- Entrenar: `scripts/entrenar_tomate.py` (YOLOv8s, 640px, batch 8, 50 épocas, corte de seguridad 85°C vía `scripts/temp_guard.py`). Reanudar: `scripts/reanudar_tomate.py`. Export ONNX (para Hailo, opset 11): `scripts/exportar_onnx.py`.

## Mejora de plagas (fases)

Modelo Tomate v1 (50 épocas) dio enfermedades foliares FUERTES (0.55-0.91 mAP50-95) pero **plagas muy débiles** (whitefly/aphid ~0.04) por el dataset de plagas de dominio equivocado (rosa/hibisco).

**Fase 1 (hecha): dominio correcto.** Se descartó `pests_aphid_thrips_whitefly` (rosa/hibisco) y se añadieron 4 datasets de plagas sobre tomate/chile real (Roboflow CC BY 4.0): `inicteluni/bemisia-tabaci-liriomyza-huidobrensis` (whitefly+leaf_miner), `pesto/tomato-pest-35mqs` (aphid/whitefly/thrips/spider_mite), `mido-kirax/chilli-disease-pest-detection-v2-w5gdk` (whitefly), `aziman-o7y1b/chili-disease-and-pest` (aphid/whitefly). Se descartan gusanos y enfermedades de chile. Tras reconstruir: whitefly 6817, aphid 1775, thrips 116 (pocos), spider_mites 3732.

**Resolución de despliegue fijada: 640px en todo** (entrenamiento 640 + HEF a 640 + inferencia 640). Debe ser consistente o las plagas pequeñas fallan por desajuste de escala. Descartada la vía 1280.

**Fase 2 (preparada): objetos diminutos sin salir de 640 vía teselado (SAHI).** El robot rebana el frame en teselas de 640 (solape 0.2), corre cada una por el HEF de 640 y junta con NMS → los insectos se ven grandes dentro de cada tesela. Inferencia: `scripts/inferir_sahi.py <imagen>`. Ideal entrenar sobre recortes de 640. Volumen para thrips/aphid: trampas amarillas (Kaggle `friso1987/yellow-sticky-traps`, Zenodo 14097660) con domain mixing moderado. Análisis en "Datasets YOLO Plagas Agrícolas.docx".

## Datos clave del reporte (PDF)

### Cultivos y objetivos de detección

**Tomate** — Plagas: mosca blanca (*Bemisia tabaci*), trips (*Frankliniella occidentalis*), minador de la hoja. Enfermedades: cáncer bacteriano (*Clavibacter michiganensis*), mancha bacteriana (*Xanthomonas* spp.), virus del rizado amarillo TYLCV. Hongos: tizón temprano (*Alternaria solani*), tizón tardío (*Phytophthora infestans*), fusariosis (*Fusarium oxysporum*).

**Melón** — Plagas: pulgón (*Aphis gossypii*), mosca blanca, trips. Enfermedades: virus del amarillamiento CYSDV, mancha angular bacteriana (*Pseudomonas syringae* pv. *lachrymans*). Hongos: oídio (*Podosphaera xanthii*), antracnosis (*Colletotrichum orbiculare*), fusariosis vascular.

**Plagas transversales de interés:** mosca blanca, pulgón, trips, minador de hoja.

### Hardware del robot

- Cómputo: Raspberry Pi 5 (+ AI HAT+ Hailo-8, 26 TOPS).
- Visión: cámara IMX219.
- Navegación: RPLIDAR C1, IMU MPU6050, SLAM con ROS 2.
- Movilidad: 6 motores DC con encoders, drivers MC33886, servos PCA9685.
- Sensores ambientales: DHT11 (temp/humedad), MQ135 (calidad de aire), sensor de pH.
- Comunicación: SIM800L (SMS/GSM), AC8265 (WiFi), LoRa (largo alcance).
- Energía: batería LiPo + panel solar con controlador de carga.
- Estructura: tubos PVC (63/110/140/150/260 mm), codos 90°/45°, piezas impresas 3D (PLA/PETG), rodamientos 608 2RS, 6 ruedas.

### Software y plataformas

- ROS 2 (nodos de sensores, control, IA y navegación), Python + C++.
- Fusion 360 (diseño 3D), Arduino Cloud (datos/alertas).

### Contexto del problema

Detección tardía de plagas/enfermedades → sobrefumigación → pérdidas económicas y daño ambiental. Origen: cultivos de papa en Linares, N.L. Alineado con ODS 2 (hambre cero), 9 (industria e innovación), 12 (consumo responsable) y 13 (acción por el clima).

### Equipo

- Dayanna Nicol Lozano Alemán — programación y documentación.
- Alonso Arath Banda Rico — programación y documentación.
- Samanta Margarita Guijarro Saucedo — electrónica y documentación.
- Luis Daniel Briones Flores — electrónica y documentación.
- Regina Monserrat González Rangel — mecánica, diseño 3D y documentación.
- Valeria Torres Castillo — mecánica, diseño 3D y documentación.
