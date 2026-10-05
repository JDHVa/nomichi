import os
import sys

from dotenv import load_dotenv
from roboflow import Roboflow

from extraer_zip_largo import extraer

DATASETS = [
    ("chili_plant_disease", "ml-vpzcc", "chili-plant-disease", 3),
    ("tom", "bryan-b56jm", "tomato-leaf-disease-ssoha", 63),
    ("plantdoc", "joseph-nelson", "plantdoc", 4),
    ("plantdoc_tomatoes", "tomatoes", "plantdoc-tomatoes", 28),
    ("pests_aphid_thrips_whitefly", "samm-v6vxt", "pests-wwm0o", 3),
    ("pest_inictel", "inicteluni", "bemisia-tabaci-liriomyza-huidobrensis", 1),
    ("pest_tomato_pesto", "pesto", "tomato-pest-35mqs", 1),
    ("pest_chili_mido", "mido-kirax", "chilli-disease-pest-detection-v2-w5gdk", 2),
    ("pest_chili_aziman", "aziman-o7y1b", "chili-disease-and-pest", 1),
]

FORMATO = "yolov8"
DEST = "datasets"


def ultima_version(project, fallback):
    try:
        numeros = []
        for v in project.versions():
            try:
                numeros.append(int(str(v.version).rstrip("/").split("/")[-1]))
            except (ValueError, AttributeError):
                continue
        if numeros:
            return max(numeros)
    except Exception as e:
        print(f"    no se pudo listar versiones ({e}); uso fallback v{fallback}")
    return fallback


def main():
    load_dotenv()
    api_key = os.environ.get("ROBOFLOW_API_KEY")
    if not api_key or api_key == "TU_API_KEY":
        print("ERROR: falta ROBOFLOW_API_KEY en .env")
        return 1

    rf = Roboflow(api_key=api_key)
    os.makedirs(DEST, exist_ok=True)

    ok, fallo = [], []
    for nombre, ws, proj, fb in DATASETS:
        destino = os.path.join(DEST, nombre)
        print(f"\n== {nombre}  ({ws}/{proj}) ==")
        if os.path.isdir(destino) and os.listdir(destino):
            print(f"    ya existe en {destino}, se omite")
            ok.append(nombre)
            continue
        try:
            project = rf.workspace(ws).project(proj)
            ver = ultima_version(project, fb)
            print(f"    descargando v{ver} -> {destino}")
            project.version(ver).download(FORMATO, location=destino)
            ok.append(nombre)
        except Exception as e:
            zip_path = os.path.join(destino, "roboflow.zip")
            if os.path.isfile(zip_path):
                print(f"    extraccion normal fallo ({e}); extrayendo con rutas largas")
                try:
                    extraer(zip_path, destino)
                    os.remove(zip_path)
                    ok.append(nombre)
                    continue
                except Exception as e2:
                    print(f"    FALLO en extraccion larga: {e2}")
                    fallo.append((nombre, str(e2)))
                    continue
            print(f"    FALLO: {e}")
            fallo.append((nombre, str(e)))

    print("\n===== RESUMEN =====")
    print(f"OK ({len(ok)}): {', '.join(ok) if ok else '-'}")
    if fallo:
        print(f"FALLARON ({len(fallo)}):")
        for n, e in fallo:
            print(f"  - {n}: {e}")
    return 0 if not fallo else 2


if __name__ == "__main__":
    sys.exit(main())
