from ultralytics import YOLO

from temp_guard import vigilar_temperatura


def main():
    model = YOLO("runs/tomate/yolov8s/weights/last.pt")
    model.add_callback("on_train_batch_end", vigilar_temperatura)
    model.train(resume=True)


if __name__ == "__main__":
    main()
