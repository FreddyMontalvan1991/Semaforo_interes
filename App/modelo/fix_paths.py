import pickle
from pathlib import Path

# Carpeta donde están los pickles
pkl_dir = Path("pickles")
pkl_file = pkl_dir / "test_fullpath.pkl"

# Ruta base donde realmente están las imágenes
# (ajústala si están en otra carpeta)
base_image_path = Path("pickles/images")

# Cargar el diccionario
with open(pkl_file, "rb") as f:
    data = pickle.load(f)

print(f"Total de registros cargados: {len(data)}")

# Construir un nuevo diccionario con rutas corregidas
new_data = {}
for rel_path, value in data.items():
    # Convertimos a ruta absoluta (o unida a la base)
    full_path = base_image_path / rel_path
    new_data[str(full_path)] = value

# Guardar el nuevo archivo
output_path = pkl_dir / "test_fullpath_fixed.pkl"
with open(output_path, "wb") as f:
    pickle.dump(new_data, f)

print(f"Archivo corregido guardado en: {output_path}")

