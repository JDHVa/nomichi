import os

BASE = "datasets/tomato_village/Variant-c(Object Detection)"
LABELS_SRC = "tv_repo/Variant-c(Object Detection)"
CLASES = [
    "Early_blight",
    "Healthy",
    "Late_blight",
    "Leaf Miner",
    "Magnesium Deficiency",
    "Nitrogen Deficiency",
    "Pottassium Deficiency",
    "Spotted Wilt Virus",
]


def normalizar_labels(split):
    src = os.path.join(LABELS_SRC, split, "yolo")
    dst = os.path.join(BASE, split, "labels")
    os.makedirs(dst, exist_ok=True)
    n, vacios = 0, 0
    for nombre in os.listdir(src):
        if not nombre.endswith(".txt"):
            continue
        lineas_out = []
        with open(os.path.join(src, nombre), encoding="utf-8", errors="ignore") as f:
            for linea in f:
                p = linea.split()
                if len(p) != 5:
                    continue
                cid = int(float(p[0]))
                lineas_out.append(f"{cid} {p[1]} {p[2]} {p[3]} {p[4]}")
        with open(os.path.join(dst, nombre), "w", encoding="utf-8") as f:
            f.write("\n".join(lineas_out))
        n += 1
        if not lineas_out:
            vacios += 1
    return n, vacios


def emparejar(split):
    imgs = os.path.join(BASE, split, "images")
    labs = os.path.join(BASE, split, "labels")
    base_img = {os.path.splitext(x)[0] for x in os.listdir(imgs)}
    base_lab = {os.path.splitext(x)[0] for x in os.listdir(labs)}
    return len(base_img), len(base_lab), len(base_img - base_lab), len(base_lab - base_img)


def main():
    for split in ("train", "val"):
        n, vacios = normalizar_labels(split)
        ni, nl, sin_lab, sin_img = emparejar(split)
        print(f"{split}: {n} labels ({vacios} vacios/negativos) | imgs {ni} labs {nl} | imgs_sin_label {sin_lab} labs_sin_img {sin_img}")

    yaml_path = "datasets/tomato_village/data.yaml"
    ruta_abs = os.path.abspath(BASE).replace("\\", "/")
    with open(yaml_path, "w", encoding="utf-8") as f:
        f.write(f"path: {ruta_abs}\n")
        f.write("train: train/images\n")
        f.write("val: val/images\n")
        f.write(f"nc: {len(CLASES)}\n")
        f.write("names:\n")
        for c in CLASES:
            f.write(f"  - {c}\n")
    print("data.yaml ->", yaml_path)


if __name__ == "__main__":
    main()
