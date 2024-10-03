import numpy as np
from PIL import Image
import os

ROOT = "/home/chanoscopio/Documents/LucasC/Imperx-2024-09-12c"

DC_per_sec = f'{ROOT}/Lucas_DC_per_sec.tiff'
dark_current_por_segundo = np.array(Image.open(DC_per_sec))
gain = f'{ROOT}/Lucas_Gain.tiff'
ganancia = np.array(Image.open(gain))

valormedio = np.mean(dark_current_por_segundo)
mediana = np.median(ganancia)
electrones_per_sec = valormedio / mediana

print(f"DC/s promedio: {valormedio}")
print(f"Mediana de la ganancia: {mediana}")
print(f"Electrones por segundo: {electrones_per_sec}")
