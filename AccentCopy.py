from PIL import Image
import os
import numpy as np
import tifffile as tiff
from scipy.stats import linregress
import re
import tqdm
from funciones import *

# Ruta a la carpeta principal que contiene las subcarpetas con las imágenes
carpeta_principal = '/home/chanoscopio/Documents/LucasC/Imagenes/2024-09-17'

# Expresión regular para extraer el tiempo de exposición del nombre de la carpeta
regex_exposicion = re.compile(r'(\d+(\.\d+)?)ms')

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
            tiempo_exposicion_ms = float(match.group(1))
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
                    # Imprime el tamaño de la imagen
                    #print(f"Tamaño de la imagen {archivo}: {imagen_np.shape}")
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

sorted_indices = np.argsort(tiempos_exposicion)

if promedios_por_pixel and varianzas_por_pixel and tiempos_exposicion:
    # Convertir listas a arrays de NumPy
    promedios_por_pixel = np.array(promedios_por_pixel)[sorted_indices]
    varianzas_por_pixel = np.array(varianzas_por_pixel)[sorted_indices]
    tiempos_exposicion = np.array(tiempos_exposicion)[sorted_indices]

    # Inicializar arrays para las pendientes y ordenadas al origen (Baseline y Squared Read Noise)
    # dark_current_por_segundo = np.zeros(promedios_por_pixel.shape[1:])
    # baseline = np.zeros(promedios_por_pixel.shape[1:])
    # thermal_noise_squared_por_segundo = np.zeros(varianzas_por_pixel.shape[1:])
    # read_noise_squared = np.zeros(varianzas_por_pixel.shape[1:])
    # r_sqd_value_int=np.zeros(promedios_por_pixel.shape[1:])
    # r_sqd_value_var=np.zeros(varianzas_por_pixel.shape[1:])
    ganancia = np.zeros(promedios_por_pixel.shape[1:])
    r_sqd_value_gan=np.zeros(varianzas_por_pixel.shape[1:])
    electrones_per_sec = np.zeros(promedios_por_pixel.shape[1:])
    #print(f"Tamaño de la variable {dark_current_por_segundo}: {dark_current_por_segundo.shape}")
    #print(f"Tamaño de la variable {baseline}: {baseline.shape}")
    #print(f"Tamaño de la variable {r_sqd_value_int}: {r_sqd_value_int.shape}")
    #print(f"Tamaño de la variable {thermal_noise_squared_por_segundo}: {thermal_noise_squared_por_segundo.shape}")
    #print(f"Tamaño de la variable {read_noise_squared}: {read_noise_squared.shape}")
    #print(f"Tamaño de la variable {r_sqd_value_var}: {r_sqd_value_var.shape}")
    
    # A = np.stack((np.ones_like(tiempos_exposicion), tiempos_exposicion)).T
    # print(f"Tamaño de la variable {A}: {A.shape}")
    # # Iterar sobre cada píxel para ajustar las rectas
    # for i in tqdm.tqdm(range(promedios_por_pixel.shape[1])):
    #     intensidades = promedios_por_pixel[:, i, :]
    #     (ordenada_int, pendiente_int), residuals_int = np.linalg.lstsq(A, intensidades)[:2]
    #     dark_current_por_segundo[i, :] = pendiente_int
    #     baseline[i, :] = ordenada_int
    #     var_int = intensidades.var(axis=0)
    #     min_var_int = np.min(var_int[var_int > 0]) if np.any(var_int > 0) else 1e-10  # Asegurarse de que no sea cero
    #     var_int[var_int == 0] = min_var_int  # Ajuste dinámico para evitar ceros
    #     if intensidades.shape[0] == 0:
    #         print("Error: No hay datos suficientes para el ajuste.")
    #     else:
    #         r_sqd_value_int[i, :] = 1 - (residuals_int / intensidades.shape[0]) / var_int
            
    #     varianzas = varianzas_por_pixel[:, i, :]
    #     (ordenada_var, pendiente_var), residuals_var = np.linalg.lstsq(A, varianzas)[:2]
    #     thermal_noise_squared_por_segundo[i, :] = pendiente_var
    #     read_noise_squared[i, :] = ordenada_var
    #     var_var = varianzas.var(axis=0)
    #     min_var_var = np.min(var_var[var_var > 0]) if np.any(var_var > 0) else 1e-10
    #     var_var[var_var == 0] = min_var_var # Ajuste dinámico
    #     if varianzas.shape[0] == 0:
    #         print("Error: No hay datos suficientes para el ajuste.")
    #     else:
    #         r_sqd_value_var[i, :]=  1 - (residuals_var / varianzas.shape[0]) / var_var
    print(varianzas_por_pixel.shape)
    print(promedios_por_pixel.shape)
    baseline, dark_current_por_segundo, r_sqd_value_int = ajuste_lineal(tiempos_exposicion, promedios_por_pixel)
    read_noise_squared, thermal_noise_squared_por_segundo, r_sqd_value_var = ajuste_lineal(tiempos_exposicion, varianzas_por_pixel)


    # Guardar las imágenes resultantes
    tiff.imwrite(os.path.join(carpeta_principal, 'Lucas_DC_per_sec.tiff'), dark_current_por_segundo.astype(np.float32))
    tiff.imwrite(os.path.join(carpeta_principal, 'Lucas_Baseline.tiff'), baseline.astype(np.float32))
    tiff.imwrite(os.path.join(carpeta_principal, 'Lucas_TN_sq_per_sec.tiff'), thermal_noise_squared_por_segundo.astype(np.float32))
    tiff.imwrite(os.path.join(carpeta_principal, 'Lucas_RN_sq.tiff'), read_noise_squared.astype(np.float32))
    tiff.imwrite(os.path.join(carpeta_principal, 'Lucas_R_sq_avg.tiff'), r_sqd_value_int.astype(np.float32))
    tiff.imwrite(os.path.join(carpeta_principal, 'Lucas_R_sq_var.tiff'), r_sqd_value_var.astype(np.float32))

# Guardar la imagen de ganancia
    #tiff.imwrite(os.path.join(carpeta_principal, 'Lucas_Gain.tiff'), ganancia.astype(np.float32))
    #tiff.imwrite(os.path.join(carpeta_principal, 'Lucas_R_sq_gain.tiff'), r_sqd_value_gan.astype(np.float32))
    

    # for i in tqdm.tqdm(range(promedios_por_pixel.shape[1])):
    #     intensidades_ganancia = promedios_por_pixel[:, i, :]
    #     varianzas_ganancia = varianzas_por_pixel[:, i, :]
    #     B = np.stack((np.ones_like(intensidades_ganancia), intensidades_ganancia))
    # # Resolver el sistema de ecuaciones lineales para obtener la pendiente y la ordenada al origen
    #     (ordenada_gan, pendiente_gan), residuals_gan = a[:2]
    
    # # Guardar la pendiente en el arreglo de ganancia
    #     ganancia[i, :] = pendiente_gan
    
    #     var_var_gan = varianzas_ganancia.var(axis=0)
    #     min_var_var_gan = np.min(var_var_gan[var_var_gan > 0])
    #     var_var_gan[var_var_gan == 0] = min_var_var_gan  # Ajuste dinámico
    
    # # Asegúrate de que residuals_gan sea un valor escalar
    #     if isinstance(residuals_gan, np.ndarray) and residuals_gan.size == 1:
    #        residuals_gan = residuals_gan.item()  # Convierte a un escalar
    #     elif isinstance(residuals_gan, np.ndarray) and residuals_gan.size == 0:
    #         residuals_gan = 1e-10  # Convierte a un escalar

    #     if intensidades_ganancia.shape[0] == 0:
    #         print("Error: No hay datos suficientes para el ajuste")
    #     else:
    #         r_sqd_value_gan[i, :] = 1 - (residuals_gan / intensidades_ganancia.shape[0]) / var_var_gan

    # tiff.imwrite(os.path.join(carpeta_principal, 'Lucas_Gain.tiff'), ganancia.astype(np.float32))
    # tiff.imwrite(os.path.join(carpeta_principal, 'Lucas_R_sq_gain.tiff'), r_sqd_value_gan.astype(np.float32))


    for i in tqdm.tqdm(range(promedios_por_pixel.shape[1])):
        for j in (range(promedios_por_pixel.shape[2])):
            intensidades_ganancia = promedios_por_pixel[:, i, j]
            varianzas_ganancia = varianzas_por_pixel[:, i, j]
            B = np.vstack([np.ones_like(intensidades_ganancia),intensidades_ganancia]).T
            (ordenada_gan, pendiente_gan), residuals_gan = np.linalg.lstsq(B, varianzas_ganancia, rcond=None)[:2]
            ganancia[i, j] = pendiente_gan
            if ganancia[i,j] == 0:
                ganancia[i,j] = 1e-10
            var_var_gan = varianzas_ganancia.var(axis=0)
            if var_var_gan == 0:
                var_var_gan = 1e-10
# Asegúrate de que residuals_gan sea un valor escalar
            if isinstance(residuals_gan, np.ndarray) and residuals_gan.size == 1:
                residuals_gan = residuals_gan.item()  # Convierte a un escalar
            if isinstance(residuals_gan, np.ndarray) and residuals_gan.size == 0:
                residuals_gan = 1e-10  # Convierte a un escalar
                
            if intensidades_ganancia.shape[0] == 0:
                print("Error: No hay datos suficientes para el ajuste")
            else:
                r_sqd_value_gan[i,j]= 1 - (residuals_gan / intensidades_ganancia.shape[0]) / var_var_gan

    tiff.imwrite(os.path.join(carpeta_principal, 'Lucas_Gain.tiff'), ganancia.astype(np.float32))
    tiff.imwrite(os.path.join(carpeta_principal, 'Lucas_R_sq_gain.tiff'), r_sqd_value_gan.astype(np.float32))

    promedios_resultados = []

# Iterar sobre todas las imágenes
    valormedio = np.mean(dark_current_por_segundo)
    mediana = np.median(ganancia)
    electrones_per_sec = valormedio / mediana

# Imprimir los 9 valores promedio resultantes
    print(f"DC/s promedio: {valormedio}")
    print(f"Mediana de la ganancia: {mediana}")
    print(f"Electrones por segundo: {electrones_per_sec}")



    # Calcular y guardar las imágenes de offset map
    for tiempo_exposicion_s in tiempos_exposicion:
        offset_map = dark_current_por_segundo * tiempo_exposicion_s + baseline
        tiempo_exposicion_ms = tiempo_exposicion_s *1000
        if tiempo_exposicion_ms.is_integer():
            archivo_offset_map = os.path.join(carpeta_principal, f'Lucas_generated_Avg_{int(tiempo_exposicion_ms)}ms.tiff')
        else:
            archivo_offset_map = os.path.join(carpeta_principal, f'Lucas_generated_Avg_{float(tiempo_exposicion_ms)}ms.tiff')
        tiff.imwrite(archivo_offset_map, offset_map.astype(np.float32))
        
        # Calcular mapa de varianza
        varianza_map = thermal_noise_squared_por_segundo * tiempo_exposicion_s + read_noise_squared
        if tiempo_exposicion_ms.is_integer():
            archivo_varianza_map = os.path.join(carpeta_principal, f'Lucas_generated_Var_{int(tiempo_exposicion_ms)}ms.tiff')
        else:
            archivo_varianza_map = os.path.join(carpeta_principal, f'Lucas_generated_Var_{float(tiempo_exposicion_ms)}ms.tiff')
        tiff.imwrite(archivo_varianza_map, varianza_map.astype(np.float32))

print("Cálculo completado. Las imágenes se han guardado en la carpeta principal.")
