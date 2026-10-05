import collections
import os
import sys

import yaml


def cargar_nombres(data_yaml):
    with open(data_yaml, encoding="utf-8") as f:
        d = yaml.safe_load(f)
    return d["names"], d.get("nc", len(d["names"]))


def auditar(base):
    nombres, nc = cargar_nombres(os.path.join(base, "data.yaml"))
    inst = collections.Counter()
    resumen = {}
    problemas = collections.Counter()
    stems_por_split = {}

    for split in ("train", "val", "test"):
        img_dir = os.path.join(base, split, "images")
        lab_dir = os.path.join(base, split, "labels")
        if not os.path.isdir(img_dir):
            continue
        imgs = [os.path.splitext(x)[0] for x in os.listdir(img_dir)]
        labs = [os.path.splitext(x)[0] for x in os.listdir(lab_dir)] if os.path.isdir(lab_dir) else []
        set_i, set_l = set(imgs), set(labs)
        stems_por_split[split] = set_i
        vacios = 0
        for lab in labs:
            p = os.path.join(lab_dir, lab + ".txt")
            n_lineas = 0
            for linea in open(p, encoding="utf-8", errors="ignore"):
                t = linea.split()
                if not t:
                    continue
                if len(t) != 5:
                    problemas["formato_incorrecto"] += 1
                    continue
                try:
                    cid = int(t[0])
                    coords = [float(x) for x in t[1:]]
                except ValueError:
                    problemas["no_numerico"] += 1
                    continue
                if cid < 0 or cid >= nc:
                    problemas["clase_fuera_rango"] += 1
                if any(c < 0 or c > 1 for c in coords):
                    problemas["coords_fuera_rango"] += 1
                inst[cid] += 1
                n_lineas += 1
            if n_lineas == 0:
                vacios += 1
        resumen[split] = {
            "imagenes": len(set_i),
            "labels": len(set_l),
            "img_sin_label": len(set_i - set_l),
            "label_sin_img": len(set_l - set_i),
            "labels_vacios_negativos": vacios,
        }

    print("===== IMAGENES POR SPLIT =====")
    for s, r in resumen.items():
        print(f"  {s}: {r}")

    splits = list(stems_por_split)
    print("\n===== FUGA ENTRE SPLITS (stems compartidos) =====")
    fuga = False
    for i in range(len(splits)):
        for j in range(i + 1, len(splits)):
            inter = stems_por_split[splits[i]] & stems_por_split[splits[j]]
            if inter:
                fuga = True
                print(f"  {splits[i]} ∩ {splits[j]}: {len(inter)}")
    if not fuga:
        print("  ninguna (0)")

    print("\n===== INSTANCIAS POR CLASE =====")
    total = sum(inst.values())
    for i, n in enumerate(nombres):
        c = inst.get(i, 0)
        pct = (100 * c / total) if total else 0
        print(f"  {i:2d} {n:32s} {c:8d}  ({pct:4.1f}%)")
    print(f"  TOTAL cajas: {total}")
    vacias = [nombres[i] for i in range(len(nombres)) if inst.get(i, 0) == 0]
    if vacias:
        print(f"  clases SIN instancias: {vacias}")

    print("\n===== PROBLEMAS DE ETIQUETAS =====")
    print(f"  {dict(problemas) if problemas else 'ninguno'}")


if __name__ == "__main__":
    auditar(sys.argv[1] if len(sys.argv) > 1 else "datasets/tomato_model")
