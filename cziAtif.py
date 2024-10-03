import czifile
import tifffile
import os

# Ruta a la carpeta que contiene los archivos .czi
carpeta_imagenes = '/home/chanoscopio/Documents/LucasC/2024-09-12'

# Función para convertir un archivo .czi a múltiples archivos .tif
def convertir_czi_a_tifs(archivo_czi, carpeta_salida):
    with czifile.CziFile(archivo_czi) as czi:
        # Obtén el stack completo (serie temporal)
        stack = czi.asarray()
    
    # Verifica la forma del stack
    print(f"Procesando: {archivo_czi}")
    print("Forma del stack:", stack.shape)
    
    # Asegúrate de que el stack tiene 5 dimensiones (T, C, Z, Y, X)
    if stack.ndim == 5:
        # Si tiene 5 dimensiones (T, C, Z, Y, X), extrae la dimensión T
        for i in range(stack.shape[0]):
            imagen = stack[i, 0, :, :, 0]  # Extrae la primera dimensión temporal y el primer canal
            archivo_tif = os.path.join(carpeta_salida, f'imagen_{i+1}.tif')
            tifffile.imwrite(archivo_tif, imagen)
            print(f"Archivo TIFF guardado en: {archivo_tif}")
    else:
        raise ValueError("El stack tiene una forma inesperada. No se puede procesar.")

# Recorre los archivos .czi en la carpeta especificada
for archivo in os.listdir(carpeta_imagenes):
    if archivo.endswith('.czi'):
        archivo_czi = os.path.join(carpeta_imagenes, archivo)
        carpeta_salida = os.path.join(carpeta_imagenes, archivo.replace('.czi', ''))
        os.makedirs(carpeta_salida, exist_ok=True)
        
        # Convierte el archivo .czi a múltiples archivos .tif
        convertir_czi_a_tifs(archivo_czi, carpeta_salida)

print("Conversión completada para todos los archivos.")
