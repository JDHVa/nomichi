import subprocess

LIMITE_TEMP = 85

_estado = {"n": 0}


def temp_gpu():
    try:
        out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
            stderr=subprocess.DEVNULL,
        )
        valores = [int(x.strip()) for x in out.decode().splitlines() if x.strip()]
        return max(valores) if valores else 0
    except Exception:
        return 0


def vigilar_temperatura(trainer):
    _estado["n"] += 1
    if _estado["n"] % 50 != 0:
        return
    t = temp_gpu()
    if t >= LIMITE_TEMP:
        print(f"[SEGURIDAD] GPU {t}C >= {LIMITE_TEMP}C: deteniendo al terminar la epoca actual")
        trainer.stop = True
