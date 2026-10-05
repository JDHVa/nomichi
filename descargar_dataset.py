import os

from dotenv import load_dotenv
from roboflow import Roboflow

load_dotenv()
api_key = os.environ.get("ROBOFLOW_API_KEY")
if not api_key:
    raise SystemExit("Falta ROBOFLOW_API_KEY en .env")

rf = Roboflow(api_key=api_key)
project = rf.workspace("joseph-nelson").project("plantdoc")
version = project.version(4)
dataset = version.download("yolov8", location="datasets/plantdoc")
print("Descargado en:", dataset.location)
