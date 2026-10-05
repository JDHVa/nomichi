import os
import shutil

from ultralytics import YOLO

RUN = "runs/detect/runs/tomate/yolov8s-3/weights/best.pt"
DEST = "modelos_entrenados"


def main():
    os.makedirs(DEST, exist_ok=True)
    model = YOLO(RUN)
    onnx = model.export(format="onnx", opset=11, imgsz=640, simplify=True, dynamic=False)
    shutil.copy2(RUN, os.path.join(DEST, "tomate_v2_640.pt"))
    shutil.copy2(onnx, os.path.join(DEST, "tomate_v2_640.onnx"))
    print("guardado en", DEST)
    print(" -", os.path.join(DEST, "tomate_v2_640.pt"))
    print(" -", os.path.join(DEST, "tomate_v2_640.onnx"))


if __name__ == "__main__":
    main()
