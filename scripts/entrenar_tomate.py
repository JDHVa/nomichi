from ultralytics import YOLO

from temp_guard import vigilar_temperatura


def main():
    model = YOLO("yolov8s.pt")
    model.add_callback("on_train_batch_end", vigilar_temperatura)
    model.train(
        data="datasets/tomato_model/data.yaml",
        epochs=50,
        imgsz=640,
        batch=8,
        device=0,
        workers=4,
        patience=20,
        project="runs/tomate",
        name="yolov8s",
        seed=0,
    )
    metrics = model.val()
    print("mAP50:", metrics.box.map50)
    print("mAP50-95:", metrics.box.map)


if __name__ == "__main__":
    main()
