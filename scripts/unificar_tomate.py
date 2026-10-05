import hashlib
import os
import re
import shutil

from PIL import Image

from extraer_zip_largo import prefijo_largo

DEST = "datasets/tomato_model"

CANON = [
    "tomato_healthy",
    "tomato_early_blight",
    "tomato_late_blight",
    "tomato_septoria",
    "tomato_leaf_mold",
    "tomato_mosaic_virus",
    "tomato_yellow_leaf_curl_virus",
    "tomato_bacterial_spot",
    "tomato_spider_mites",
    "tomato_leaf_miner",
    "tomato_spotted_wilt_virus",
    "tomato_magnesium_deficiency",
    "tomato_nitrogen_deficiency",
    "tomato_potassium_deficiency",
    "whitefly",
    "aphid",
    "thrips",
]
IDX = {n: i for i, n in enumerate(CANON)}

TOM = {
    0: "tomato_early_blight",
    1: "tomato_healthy",
    2: "tomato_late_blight",
    3: "tomato_leaf_miner",
    4: "tomato_leaf_mold",
    5: "tomato_mosaic_virus",
    6: "tomato_septoria",
    7: "tomato_spider_mites",
    8: "tomato_yellow_leaf_curl_virus",
}
PLANTDOC = {
    19: "tomato_early_blight",
    20: "tomato_septoria",
    21: "tomato_bacterial_spot",
    22: "tomato_late_blight",
    23: "tomato_mosaic_virus",
    24: "tomato_yellow_leaf_curl_virus",
    25: "tomato_healthy",
    26: "tomato_leaf_mold",
    27: "tomato_spider_mites",
}
VILLAGE = {
    0: "tomato_early_blight",
    1: "tomato_healthy",
    2: "tomato_late_blight",
    3: "tomato_leaf_miner",
    4: "tomato_magnesium_deficiency",
    5: "tomato_nitrogen_deficiency",
    6: "tomato_potassium_deficiency",
    7: "tomato_spotted_wilt_virus",
}
INICTEL = {0: "whitefly", 1: "tomato_leaf_miner"}
PESTO = {2: "aphid", 3: "whitefly", 6: "thrips", 7: "tomato_spider_mites"}
CHILI_MIDO = {4: "whitefly"}
CHILI_AZIMAN = {1: "aphid", 5: "whitefly"}

SOURCES = [
    {"name": "tom", "map": TOM, "require_box": False,
     "dirs": ["datasets/tom/train", "datasets/tom/valid", "datasets/tom/test"]},
    {"name": "plantdoc", "map": PLANTDOC, "require_box": True,
     "dirs": ["datasets/plantdoc/train", "datasets/plantdoc/valid", "datasets/plantdoc/test"]},
    {"name": "village", "map": VILLAGE, "require_box": False,
     "dirs": ["datasets/tomato_village/Variant-c(Object Detection)/train",
              "datasets/tomato_village/Variant-c(Object Detection)/val"]},
    {"name": "inictel", "map": INICTEL, "require_box": True,
     "dirs": ["datasets/pest_inictel/train", "datasets/pest_inictel/test"]},
    {"name": "pesto", "map": PESTO, "require_box": True,
     "dirs": ["datasets/pest_tomato_pesto/train", "datasets/pest_tomato_pesto/valid",
              "datasets/pest_tomato_pesto/test"]},
    {"name": "chilimido", "map": CHILI_MIDO, "require_box": True,
     "dirs": ["datasets/pest_chili_mido/train", "datasets/pest_chili_mido/valid",
              "datasets/pest_chili_mido/test"]},
    {"name": "chiliaziman", "map": CHILI_AZIMAN, "require_box": True,
     "dirs": ["datasets/pest_chili_aziman/train", "datasets/pest_chili_aziman/valid",
              "datasets/pest_chili_aziman/test"]},
]

EXT = (".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG")


def base_original(stem):
    s = re.split(r"\.rf\.", stem)[0]
    s = re.sub(r"_aug\d+$", "", s)
    s = re.sub(r"_(jpg|jpeg|png|JPG|JPEG|PNG)$", "", s)
    return s


def split_de_grupo(clave):
    h = int(hashlib.md5(clave.encode("utf-8")).hexdigest(), 16) % 1000
    if h < 800:
        return "train"
    if h < 950:
        return "val"
    return "test"


def remap_label(path, mapa):
    lineas = []
    lp = prefijo_largo(path)
    if os.path.isfile(lp):
        with open(lp, encoding="utf-8", errors="ignore") as f:
            for linea in f:
                p = linea.split()
                if len(p) != 5:
                    continue
                nombre = mapa.get(int(float(p[0])))
                if nombre is None:
                    continue
                lineas.append(f"{IDX[nombre]} {p[1]} {p[2]} {p[3]} {p[4]}")
    return lineas


def imagen_valida(path):
    try:
        with Image.open(prefijo_largo(path)) as im:
            im.verify()
        return True
    except Exception:
        return False


def enlazar(src, dst):
    lp = prefijo_largo(src)
    try:
        os.link(lp, dst)
    except OSError:
        shutil.copy2(lp, dst)


def main():
    if os.path.isdir(DEST):
        shutil.rmtree(DEST)
    for split in ("train", "val", "test"):
        os.makedirs(os.path.join(DEST, split, "images"), exist_ok=True)
        os.makedirs(os.path.join(DEST, split, "labels"), exist_ok=True)

    contadores = {"train": 0, "val": 0, "test": 0}
    saltadas = 0
    corruptas = 0
    for src in SOURCES:
        n = 0
        for base in src["dirs"]:
            img_dir = os.path.join(base, "images")
            lab_dir = os.path.join(base, "labels")
            if not os.path.isdir(prefijo_largo(img_dir)):
                continue
            for img in os.listdir(prefijo_largo(img_dir)):
                if not img.endswith(EXT):
                    continue
                stem, ext = os.path.splitext(img)
                lineas = remap_label(os.path.join(lab_dir, stem + ".txt"), src["map"])
                if src["require_box"] and not lineas:
                    saltadas += 1
                    continue
                if not imagen_valida(os.path.join(img_dir, img)):
                    corruptas += 1
                    continue
                clave = f"{src['name']}/{base_original(stem)}"
                split = split_de_grupo(clave)
                nuevo = f"{src['name']}_{n:06d}"
                n += 1
                enlazar(os.path.join(img_dir, img), os.path.join(DEST, split, "images", nuevo + ext.lower()))
                with open(os.path.join(DEST, split, "labels", nuevo + ".txt"), "w", encoding="utf-8") as f:
                    f.write("\n".join(lineas))
                contadores[split] += 1

    ruta_abs = os.path.abspath(DEST).replace("\\", "/")
    with open(os.path.join(DEST, "data.yaml"), "w", encoding="utf-8") as f:
        f.write(f"path: {ruta_abs}\n")
        f.write("train: train/images\n")
        f.write("val: val/images\n")
        f.write("test: test/images\n")
        f.write(f"nc: {len(CANON)}\n")
        f.write("names:\n")
        for name in CANON:
            f.write(f"  - {name}\n")

    print("split por grupo (base original, sin fuga):", contadores)
    print("saltadas (sin caja de tomate):", saltadas)
    print("saltadas (imagen corrupta):", corruptas)


if __name__ == "__main__":
    main()
