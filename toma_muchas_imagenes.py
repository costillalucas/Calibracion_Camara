

import matplotlib.pyplot as plt
from driver_imperx import ky, ImperxCamera
from driver_imperx import *

#IMPORTANTE: el offset en x va en múltiplos de 32 y el offset de y va en múltiplos de 2
#roi = ((pixel_inicial_x, pixel_inicial_y), (pixel_final_x, pixel_final_y))
#para calcular el ancho: width = pixel_final_x - pixel_inicial_x ; el alto: height = pixel_final_y - pixel_inicial_y
roi_nuestro = ((4064,2528), (5280, 4448))

# Indique la ruta en donde quiere crear las subcarpetas en donde serán guardadas las imagenes tomadas a cada tiempo de exposicion
ROOT = '/home/chanoscopio/Documents/LucasC/Imagenes/2024-10-03-12bit'

#Si tomo más de 16 imágenes se cuelga, esto seguramente es por el buffer del grabber que debe estar configurado para almacenar 16 imágenes 
#ARREGLADO, puedo tomar la cantidad de imágenes que se requiera. Solo debemos pasar el parámetro n_frames al inicializar el objeto imperx
n_imagenes = 3

# Probaremos ahora la configuracion, a ver si la toma 
config = '/home/chanoscopio/Documents/LucasC/Programas/IpxCxp_CheetahGmax_010003.xml'

handle = ky.KYFG_Init()
imperx = ImperxCamera(roi=roi_nuestro, n_frames=n_imagenes, config_xml=config)

#Tiempos de exposicion en microsegundos, donde no puede ser menor a 10 ni mayor 291000.
# Los escribo como múltiplos de 1000 para que queden en milisegundos y sus nombres de carpetas sean accesibles para el Accent
#Hay un problema, al tomar las fotos toma con el tiempo de exposicion de la foto anterior, no con el nuevo
#ARREGLADO, al poner un sleep de 300ms luego de setear el tiempo de exposicion ya toma imágenes como queremos
tiempos_de_exposicion = [50000, 100000, 150000, 200000]

#Ganancia debe estar como flotante sino da error
ganancia = 1.00

guardar_imagenes(imperx, n_imagenes, ganancia, tiempos_de_exposicion, ROOT)

# try: 
#     var_blanco = []
#     means_blanco = []
#     exp_times = np.linspace(40000.0, 80000.0, 2)
#     exp_times = [15.0]
#     for i, tiempo_exp in enumerate(exp_times):
#         for j in range(600):
#             imperx.set_gain_exposure(1.25, int(round(tiempo_exp, 1)))
#             sleep(0.5)
#             imagen = imperx.get_frame(2)
#             imperx.queue.queue.clear()
#             print(i)
#        # plt.imshow(imagen)
#        # plt.show()





      #  var, mean = toma1(tiempo_exp)
      #  var_blanco.append(var)
      #  means_blanco.append(mean)
      #  print("t_exp", tiempo_exp)
#  im_mean = np.zeros(shape = (7000, 9344))
#  im_var = np.zeros(shape = (7000, 9344))
#  xcuad = np.zeros(shape = (7000, 9344))
   #     im_mean, im_var = mean_movil(tiempo_exp, n_imagenes) 
        #np.save("ruido_total/uniforme_exp_time" + str(tiempo_exp) + "_" + str(j), imagen) 

        #np.save("matricesMVLD/light/var_"+str(round(tiempo_exp)), im_var) 
        #np.save("matricesMVLD/light/mean_"+str(round(tiempo_exp)), im_mean) 
   # np.save("ruido_total/tiempo_de_exp_1", exp_times) 

   #     imperx.set_gain_exposure(1.25, int(round(tiempo_exp, 1)))
   #     sleep(0.05)
   #     for j in range(n_imagenes):
   #         imagen = imperx.get_frame(2)
   #         imperx.queue.queue.clear()
   #         im_mean = (imagen/n_imagenes + im_mean)
   #         xcuad = np.multiply(imagen,imagen)/n_imagenes + xcuad 
   #      #   np.save("oscuridad_por_pixel_full/im_exp_"+str(round(tiempo_exp, 0))+'_'+str(j+1), imagen)
   #         print("imagen", j , "tiempo de exposicion", i, round(tiempo_exp, 0))
   #     im_var = xcuad - np.multiply(im_mean,im_mean)

   #     np.save("oscuridad_full_2/im_mean_" + str(tiempo_exp), im_mean)
   #     np.save("oscuridad_full_2/im_var_"+ str(tiempo_exp), im_var)
   # np.save("oscuridad_full_2/exp_times_2", exp_times)

    #np.save("oscuridad_por_pixel_full/exp_times", np.round(exp_times, 0))
   
   # np.save("means_oscuridad_fullframe", means)
   # np.save("stds_oscuridad_fullframe", stds)
    #np.save("tiempos_de_exposicion_oscuridad_fullframe_1", exp_times)
# except Exception as e:
#     print("exception:", str(e))
#     print(traceback.format_exc())
# finally:
#         imperx.close()
