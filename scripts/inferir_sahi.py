import sys

from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction

PESOS = "runs/detect/runs/tomate/yolov8s/weights/best.pt"


def main():
    if len(sys.argv) < 2:
        print("uso: inferir_sahi.py <imagen> [salida_dir]")
        return 1
    imagen = sys.argv[1]
    salida = sys.argv[2] if len(sys.argv) > 2 else "runs/sahi"

    modelo = AutoDetectionModel.from_pretrained(
        model_type="ultralytics",
        model_path=PESOS,
        confidence_threshold=0.25,
        device="cuda:0",
    )
    resultado = get_sliced_prediction(
        imagen,
        modelo,
        slice_height=640,
        slice_width=640,
        overlap_height_ratio=0.2,
        overlap_width_ratio=0.2,
    )
    resultado.export_visuals(export_dir=salida)
    print(f"detecciones: {len(resultado.object_prediction_list)}")
    for o in resultado.object_prediction_list:
        print(f"  {o.category.name}  conf={o.score.value:.2f}  bbox={o.bbox.to_xyxy()}")
    print("visual guardado en:", salida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
