import os
from PIL import Image
import numpy as np

# Definimos la función para cargar una imagen y convertirla a un array de NumPy
def load_image_as_array(image_path):
    try:
        image = Image.open(image_path)
        image_array = np.asarray(image)
        return image_array
    except Exception as e:
        print(f"Error al cargar la imagen {image_path}: {e}")
        return None

# Definimos la función para comparar dos imágenes y calcular las 5 diferencias más grandes y sus localizaciones
def compare_images(image1_path, image2_path, rtol=1.e-3, atol=1.e-2, equal_nan=False):
    image1_array = load_image_as_array(image1_path)
    image2_array = load_image_as_array(image2_path)
    
    if image1_array is None or image2_array is None:
        return False, None
    
    # Crear una máscara para los valores válidos (no NaN)
    valid_mask = ~np.isnan(image1_array) & ~np.isnan(image2_array)
    
    # Calcula las diferencias solo en las ubicaciones válidas
    diff_array = np.abs(image1_array - image2_array)
    valid_diff_array = np.where(valid_mask, diff_array, 0)
    
    # Verifica si las imágenes están dentro de la tolerancia, ignorando NaN
    are_close = np.allclose(image1_array[valid_mask], image2_array[valid_mask], rtol=rtol, atol=atol, equal_nan=equal_nan)
    
    # Aplanar la matriz para encontrar los valores más altos
    flattened_diff = valid_diff_array.flatten()
    
    # Ordenar las diferencias en orden descendente, ignorando NaN
    sorted_indices = np.argsort(flattened_diff)[::-1]
    
    # Encontrar las 5 diferencias más grandes y sus ubicaciones
    top_diffs = []
    for k in range(min(10, len(sorted_indices))):
        index = sorted_indices[k]
        diff_value = flattened_diff[index]
        if not np.isnan(diff_value):  # Ignorar diferencias NaN
            diff_location = np.unravel_index(index, valid_diff_array.shape)
            top_diffs.append((diff_value, diff_location))
    
    return are_close, top_diffs

# Ruta de la carpeta donde están las imágenes
folder_path = '/home/chanoscopio/Documents/LucasC/Imagenes/2024-09-17'

# Obtener una lista de todos los archivos en la carpeta
all_files = os.listdir(folder_path)

# Filtrar las imágenes que empiezan con "Lucas_"
lucas_images = [f for f in all_files if f.startswith("Lucas_")]

# Inicializar listas para resultados
diferentes = []
iguales = []

# Recorrer las imágenes con prefijo "Lucas_"
for lucas_image in lucas_images:
    # Nombre de la imagen sin el prefijo "Lucas_"
    original_image_name = lucas_image.replace("Lucas_", "", 1)
    
    # Verificar si la imagen sin prefijo existe
    if original_image_name in all_files:
        lucas_image_path = os.path.join(folder_path, lucas_image)
        original_image_path = os.path.join(folder_path, original_image_name)
        
        # Comparar las dos imágenes y obtener las 5 diferencias más grandes
        are_images_close, top_diffs = compare_images(lucas_image_path, original_image_path)
        
        # Acumular resultados
        if are_images_close:
            iguales.append((lucas_image, original_image_name, top_diffs))
        else:
            diferentes.append((lucas_image, original_image_name, top_diffs))
    else:
        print(f"No se encontró una imagen correspondiente para '{lucas_image}'")

# Mostrar resultados al final
print("\nResultados:")
if iguales:
    print("Imágenes que son iguales (dentro de la tolerancia):")
    for img1, img2, top_diffs in iguales:
        print(f"  - {img1} y {img2}, 5 diferencias más grandes:")
        for diff_value, diff_location in top_diffs:
            print(f"    - Diferencia: {diff_value} en {diff_location}")
else:
    print("No se encontraron imágenes iguales dentro de la tolerancia especificada.")

if diferentes:
    print("\nImágenes que son diferentes:")
    for img1, img2, top_diffs in diferentes:
        print(f"  - {img1} y {img2}, 5 diferencias más grandes:")
        for diff_value, diff_location in top_diffs:
            print(f"    - Diferencia: {diff_value} en {diff_location}")
else:
    print("No se encontraron imágenes diferentes dentro de la tolerancia especificada.")
