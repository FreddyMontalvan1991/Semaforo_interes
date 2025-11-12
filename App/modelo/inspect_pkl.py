import pickle
from pathlib import Path

pkl_path = Path("pickles/test_fullpath.pkl")

with open(pkl_path, "rb") as f:
    data = pickle.load(f)

print(f"Tipo de objeto cargado: {type(data)}")

# Si es un dict, muestra las claves
if isinstance(data, dict):
    print("Claves encontradas:", data.keys())

# Si es lista, muestra la longitud y un ejemplo
elif isinstance(data, list):
    print(f"Tamaño del dataset: {len(data)}")
    print("Ejemplo de primer elemento:", data[0])
else:
    print("Contenido desconocido:", data)
