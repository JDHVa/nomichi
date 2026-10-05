import sys

from ultralytics import YOLO

PESOS = "runs/detect/runs/tomate/yolov8s-3/weights/best.pt"


def main():
    source = sys.argv[1] if len(sys.argv) > 1 else "datasets/tomato_model/test/images"
    if source == "0":
        source = 0
    conf = float(sys.argv[2]) if len(sys.argv) > 2 else 0.35
    model = YOLO(PESOS)
    model.predict(
        source=source,
        conf=conf,
        save=True,
        project="runs/pruebas",
        name="pred",
        line_width=2,
        show=(source == 0),
    )
    print("resultados guardados en runs/pruebas/")


if __name__ == "__main__":
    main()
