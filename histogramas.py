import os
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

ROOT = "/home/chanoscopio/Documents/LucasC/Imagenes/2024-09-17"

# Cargar la imagen como un array de NumPy
imagenes = [
    "Baseline",
    "DC_per_sec",
    "RN_sq",
    "TN_sq_per_sec",
    "Gain",
]

fig, axs = plt.subplots(1, 5, figsize=(16, 4), constrained_layout=True, sharey=True)
lmin = 5
for ndx, imagen in enumerate(imagenes):
    nombre = f"{ROOT}/{imagen}.tiff"
    print(ndx, nombre)
    Imagen_array = np.array(Image.open(nombre))
    data = Imagen_array.flatten()

    # Configuración del histograma
    n_bins = 25

# Crear la figura y los subplots
    (x_min, x_max) = np.percentile(data, [lmin,100-lmin])
    print(x_min, x_max)
    filtered_data = data[(data >= x_min) & (data <= x_max)]
# Cumulative distribution function (CDF)
    axs[ndx].ecdf(filtered_data)
    # n, bins, patches = axs[ndx].hist(data, n_bins, density=True, histtype='step', cumulative=True, label='Cumulative histogram')
    # x = np.linspace(data.min(), data.max(), 1000)
    # mu = np.mean(data)  # Media calculada a partir de los datos
    # sigma = np.std(data)  # Desviación estándar calculada a partir de los datos
    # x = np.linspace((mu - 3 * sigma), (mu + 3 * sigma), 1000)
    # y = (1 / (np.sqrt(2 * np.pi) * sigma)) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)
    # y = y.cumsum()
    # y /= y[-1]
    
    # axs[ndx].plot(x, y, 'k--', linewidth=1.5, label='CDF')
    axs[ndx].grid(True)
    axs[ndx].legend()

axs[0].set_xlabel('Baseline - Pixel Offset (counts)')
axs[1].set_xlabel('Dark Current (counts/s)')
axs[2].set_xlabel('Read Noise square(counts^2)')
axs[4].set_xlabel('Gain - Varianza/Media (counts/electron)')
axs[3].set_xlabel('Thermal Noise square (counts^2/s)')
axs[0].set_ylabel('Probabilidad acumulada')
# Mostrar el gráfico
plt.suptitle(f"Distribuciones acumulativas obtenidas por caractarizacion libre de fotones ({lmin}-{100-lmin})")
plt.show()

# # def load_image_as_array(image_path):
# #     try:
# #         image = Image.open(image_path)
# #         image_array = np.asarray(image)
# #         return image_array
# #     except Exception as e:
# #         print(f"Error al cargar la imagen {image_path}: {e}")
# #         return None
    
# # # Ruta de la carpeta donde están las imágenes
# # folder_path = '/home/chanoscopio/Documents/LucasC/2024-08-28/'

# # # Obtener una lista de todos los archivos en la carpeta
# # all_files = os.listdir(folder_path)

# # # Filtrar las imágenes que empiezan con "Lucas_"
# # lucas_images = [f for f in all_files if f.startswith("Lucas_")]


