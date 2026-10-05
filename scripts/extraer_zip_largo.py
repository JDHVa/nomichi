import os
import sys
import zipfile


def prefijo_largo(ruta):
    ruta = os.path.abspath(ruta).replace("/", "\\")
    if ruta.startswith("\\\\?\\"):
        return ruta
    if ruta.startswith("\\\\"):
        return "\\\\?\\UNC\\" + ruta[2:]
    return "\\\\?\\" + ruta


def extraer(zip_path, destino):
    os.makedirs(destino, exist_ok=True)
    with zipfile.ZipFile(zip_path) as z:
        nombres = z.namelist()
        total = len(nombres)
        for i, nombre in enumerate(nombres, 1):
            destino_rel = nombre.replace("/", os.sep)
            salida = os.path.join(destino, destino_rel)
            salida_larga = prefijo_largo(salida)
            if nombre.endswith("/"):
                os.makedirs(salida_larga, exist_ok=True)
                continue
            os.makedirs(prefijo_largo(os.path.dirname(salida)), exist_ok=True)
            with z.open(nombre) as src, open(salida_larga, "wb") as dst:
                dst.write(src.read())
            if i % 500 == 0 or i == total:
                print(f"  {i}/{total}")
    print(f"OK: {total} archivos -> {destino}")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("uso: extraer_zip_largo.py <zip> <destino>")
        sys.exit(1)
    extraer(sys.argv[1], sys.argv[2])
