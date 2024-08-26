from PIL import Image
import os
import numpy as np
import tifffile as tiff
from scipy.stats import linregress
import re
import tqdm

# Ruta a la carpeta principal que contiene las subcarpetas con las imágenes
carpeta_principal = '/home/chanoscopio/Documents/LucasC/2024-08-14'

# Expresión regular para extraer el tiempo de exposición del nombre de la carpeta
regex_exposicion = re.compile(r'(\d+)ms')

# Listas para almacenar los tiempos de exposición, promedios y varianzas por píxel
tiempos_exposicion = []
promedios_por_pixel = []
varianzas_por_pixel = []

# Itera sobre las subcarpetas en la carpeta principal
for subcarpeta in os.listdir(carpeta_principal):
    ruta_subcarpeta = os.path.join(carpeta_principal, subcarpeta)
    if os.path.isdir(ruta_subcarpeta):
        # Extrae el tiempo de exposición del nombre de la subcarpeta
        match = regex_exposicion.search(subcarpeta)
        if match:
            tiempo_exposicion_ms = int(match.group(1))
            tiempo_exposicion_s = tiempo_exposicion_ms / 1000.0  # Convertir a segundos
            tiempos_exposicion.append(tiempo_exposicion_s)
            
            # Lista para almacenar las imágenes en formato NumPy
            imagenes_np = []
            
            # Itera sobre los archivos en la subcarpeta
            for archivo in os.listdir(ruta_subcarpeta):
                if archivo.endswith('.tif'):
                    # Carga la imagen .tif
                    imagen = Image.open(os.path.join(ruta_subcarpeta, archivo))
                    imagen_np = np.array(imagen)  # Convierte la imagen a un array de NumPy
                    imagenes_np.append(imagen_np)
            
            if imagenes_np:
                # Convierte la lista de imágenes en un array 3D (número de imágenes, ancho, alto)
                stack_imagenes = np.stack(imagenes_np, axis=0)
                
                # Calcula el promedio y la varianza de la intensidad de cada píxel
                promedio_intensidad = np.mean(stack_imagenes, axis=0)
                varianza_intensidad = np.var(stack_imagenes, axis=0)
                
                # Añadir el promedio y la varianza a las listas
                promedios_por_pixel.append(promedio_intensidad)
                varianzas_por_pixel.append(varianza_intensidad)
                
                # Guardar las imágenes de intensidad promedio y varianza para este tiempo de exposición
                archivo_tif_promedio = os.path.join(carpeta_principal, f'Lucas_Avg_{subcarpeta}.tiff')
                tiff.imwrite(archivo_tif_promedio, promedio_intensidad.astype(np.float32))
                
                archivo_tif_varianza = os.path.join(carpeta_principal, f'Lucas_Var_{subcarpeta}.tiff')
                tiff.imwrite(archivo_tif_varianza, varianza_intensidad.astype(np.float32))

if promedios_por_pixel and varianzas_por_pixel and tiempos_exposicion:
    # Convertir listas a arrays de NumPy
    promedios_por_pixel = np.array(promedios_por_pixel)
    varianzas_por_pixel = np.array(varianzas_por_pixel)
    tiempos_exposicion = np.array(tiempos_exposicion)
    
    # Inicializar arrays para las pendientes y ordenadas al origen (Baseline y Squared Read Noise)
    dark_current_por_segundo = np.zeros(promedios_por_pixel.shape[1:])
    baseline = np.zeros(promedios_por_pixel.shape[1:])
    thermal_noise_squared_por_segundo = np.zeros(varianzas_por_pixel.shape[1:])
    read_noise_squared = np.zeros(varianzas_por_pixel.shape[1:])
    r_sqd_value_int=np.zeros(promedios_por_pixel.shape[1:])
    r_sqd_value_var=np.zeros(varianzas_por_pixel.shape[1:])

    # Iterar sobre cada píxel para ajustar las rectas
    for i in tqdm.tqdm(range(promedios_por_pixel.shape[1])):
        for j in tqdm.tqdm(range(promedios_por_pixel.shape[2]), leave=False):
            # Ajuste para la intensidad promedio
            intensidades = promedios_por_pixel[:, i, j]
            pendiente_int, ordenada_int, rvalue_int, _, _ = linregress(tiempos_exposicion, intensidades)
            dark_current_por_segundo[i, j] = pendiente_int
            baseline[i, j] = ordenada_int
            r_sqd_value_int[i, j]=(rvalue_int**2)
            
            # Ajuste para la varianza
            varianzas = varianzas_por_pixel[:, i, j]
            pendiente_var, ordenada_var, rvalue_var, _, _ = linregress(tiempos_exposicion, varianzas)
            thermal_noise_squared_por_segundo[i, j] = pendiente_var
            read_noise_squared[i, j] = ordenada_var
            r_sqd_value_var[i, j]=(rvalue_var**2)
    
    # Guardar las imágenes resultantes
    tiff.imwrite(os.path.join(carpeta_principal, 'Lucas_DC_per_sec.tiff'), dark_current_por_segundo.astype(np.float32))
    tiff.imwrite(os.path.join(carpeta_principal, 'Lucas_Baseline.tiff'), baseline.astype(np.float32))
    tiff.imwrite(os.path.join(carpeta_principal, 'Lucas_TN_sq_per_sec.tiff'), thermal_noise_squared_por_segundo.astype(np.float32))
    tiff.imwrite(os.path.join(carpeta_principal, 'Lucas_RN_sq.tiff'), read_noise_squared.astype(np.float32))
    tiff.imwrite(os.path.join(carpeta_principal, 'Lucas_R_sq_avg.tiff'), r_sqd_value_int.astype(np.float32))
    tiff.imwrite(os.path.join(carpeta_principal, 'Lucas_R_sq_var.tiff'), r_sqd_value_var.astype(np.float32))
    
    # Calcular y guardar las imágenes de offset map
    for tiempo_exposicion_s in tiempos_exposicion:
        offset_map = dark_current_por_segundo * tiempo_exposicion_s + baseline
        archivo_offset_map = os.path.join(carpeta_principal, f'Lucas_generated_Avg_{int(tiempo_exposicion_s * 1000)}ms.tiff')
        tiff.imwrite(archivo_offset_map, offset_map.astype(np.float32))
        
        # Calcular mapa de varianza
        varianza_map = thermal_noise_squared_por_segundo * tiempo_exposicion_s + read_noise_squared
        archivo_varianza_map = os.path.join(carpeta_principal, f'Lucas_generated_Var_{int(tiempo_exposicion_s * 1000)}ms.tiff')
        tiff.imwrite(archivo_varianza_map, varianza_map.astype(np.float32))

print("Cálculo completado. Las imágenes se han guardado en la carpeta principal.")
