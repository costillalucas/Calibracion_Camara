import sys
import os
sys.path.insert(0, os.environ['KAYA_VISION_POINT_PYTHON_PATH'])

import KYFGLib as ky
import ctypes
import traceback
import numpy as np 
import matplotlib.pyplot as plt 
from abc import ABC, abstractmethod
from typing import Tuple, Optional

import tifffile as tiff
from time import sleep, time, perf_counter
import sys
import os
import threading
import queue

#Roi = Tuple[int, int]
Roi = Tuple[Tuple[int, int], Tuple[int, int]]


class Camera(ABC):
    @abstractmethod
    def __init__(self, bit_depth: int = 8, roi: Optional[Roi] = None):
        pass

    @abstractmethod
    def set_gain_exposure(self, gain: int, exposure: int):
        pass

    @abstractmethod
    def get_frame(self) -> np.ndarray:
        pass

class ImperxCamera(Camera):

    _is_camera_open = False

    def __init__(self, bit_depth: int = 8, roi: Optional[Roi] = None):
        inicio_init = perf_counter()
        self.grabber_index = 0 #número del grabber de la lista de grabbers
        self.max_boards = 4
        self.max_cams = 4
        self.device_queued_buffers_supported = "FW_DmaCapable_QueuedBuffers_Imp"

        self.init_params = ky.KYFGLib_InitParameters()
        self.connection = -1
        self.stream_info_struct = self.StreamInfoStruct()
        self.cam_handle_array = [[0 for x in range(0)] for y in range(self.max_boards)]
        self.handle = [0 for i in range(self.max_boards)]
        self.camera_stream_handle = 0
        self.frame_data_size = 0
        self.frame_data_aligment = 0
        self.stream_buffer_handle = [0 for i in range(16)]
        self.stream_alligned_buffer = [0 for i in range(16)]
        self._max_image_width = 9344
        self._max_image_height = 7000
        self.n_frames = 1
        self.camera_index = 0
        self.image = 0 
        self._stream_callback_func.__func__.data = 0
        self._stream_callback_func.__func__.copyingDataFlag = 0
        self._time_stamp = 0
        self.image_offset_x = None
        self.image_offset_y = None
        self.image_width = None
        self.image_height = None
        self.image_array = np.array([])


        #colas
        self.queue = queue.Queue(10)

        ky.KYFGLib_Initialize(self.init_params)
        inicio_grabber = perf_counter()
        self._connect_to_grabber()
        final_grabber = perf_counter()
        print("grabber: ", final_grabber - inicio_grabber)
        inicio_camera = perf_counter()
        self._connect_to_camera()
        final_camera = perf_counter()
        print("camara: ", final_camera - inicio_camera)
        self._set_roi(roi)

        _, self.exposure_time =  ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "ExposureTime")
        _, self.gain = ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "Gain")

        #Para poder poner mayores tiempos de exposición
        ky.KYFG_SetCameraValue(self.cam_handle_array[self.grabber_index][0], "AcquisitionFrameRateEnable", True)

        #La configuración de los bits del adc y del color puede cambiar si se abre la app de vision point
        #si se quiere cambiar el bit depht o el pixel format hay que cambiar el tipo de dato que aparece
        #en la función _stream_callback_func en data = np.frombuffer(buffer_byte_array, dtype=np.int16)
        # a data = np.frombuffer(buffer_byte_array, dtype=np.uint8)
        ky.KYFG_SetCameraValue(self.cam_handle_array[self.grabber_index][0], "AdcBitDepth", "Bit12")
        ky.KYFG_SetCameraValue(self.cam_handle_array[self.grabber_index][0], "PixelFormat", "Mono12")
        self.bit_depth = ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "AdcBitDepth")
        self.pixel_format = ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "PixelFormat")
        print("Bit Depth ADC:",self.bit_depth)
        print("Bit PixelFormat:",self.pixel_format)

        #seteamos el modo de exposición
        ky.KYFG_SetCameraValue(self.cam_handle_array[self.grabber_index][0], "ExposureAuto", "Off")
        ky.KYFG_SetCameraValue(self.cam_handle_array[self.grabber_index][0], "TriggerMode", "Off")
        ky.KYFG_SetCameraValue(self.cam_handle_array[self.grabber_index][0], "ExposureMode", "Timed")
        _, _, self.exposure_mode = ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "ExposureMode")
        print(ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "TriggerMode"))
        print(ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "ExposureAuto"))
        print(self.exposure_mode)

        _, self.camera_stream_handle = ky.KYFG_StreamCreate(self.cam_handle_array[self.grabber_index][0], 0)

        _, = ky.KYFG_StreamBufferCallbackRegister(self.camera_stream_handle, self._stream_callback_func, ky.py_object(self.stream_info_struct))

        self._allocate_memory()

        final_init = perf_counter()
        print("tiempo init: ", final_init - inicio_init)

    def _connect_to_grabber(self):
        _, fg_amount = ky.KY_DeviceScan()
        _, dev_info = ky.KY_DeviceInfo(self.grabber_index)
        try:
            self.connection = self._set_grabber_connection()
        except ky.KYException as err:
            print("Error al conectar con el frame grabber")
        return



    def _set_grabber_connection(self):
        self.handle
        connected_fghandle, = ky.KYFG_Open(self.grabber_index)
        connected = connected_fghandle.get()
        self.handle[self.grabber_index] = connected
        ky.KYFG_GetGrabberValueInt(self.handle[self.grabber_index], self.device_queued_buffers_supported)
        return 0

    def _connect_to_camera(self):
        _, self.cam_handle_array[self.grabber_index] = ky.KYFG_UpdateCameraList(self.handle[self.grabber_index])
        cams_num = len(self.cam_handle_array[self.grabber_index])
        if (cams_num < 1):
            print("No se encontraron camaras")
        
        # ACA VA EL XML
        KYFG_CameraOpen2_status, = ky.KYFG_CameraOpen2(self.cam_handle_array[self.grabber_index][0], None)
        if KYFG_CameraOpen2_status == ky.FGSTATUS_OK:
            print("Camara conectada correctamente")
            self._is_camera_open = True

    def _set_roi(self, roi):
        if roi is None:
            _, = ky.KYFG_SetCameraValueInt(self.cam_handle_array[self.grabber_index][0], "Width", self._max_image_width)
            _, = ky.KYFG_SetCameraValueInt(self.cam_handle_array[self.grabber_index][0], "Height", self._max_image_height)
            self.image_offset_x = 0
            self.image_offset_y = 0
            self.image_width = self._max_image_width
            self.image_height = self._max_image_height


        else: 
            self.image_offset_x = roi[0][0]
            self.image_offset_y = roi[0][1]
            self.image_width = roi[1][0] - roi[0][0]
            self.image_height = roi[1][1] - roi[0][1]
            print("height", type(self.image_height), self.image_height)
            print("width", type(self.image_width), self.image_width)
            print("offset x", type(self.image_offset_x), self.image_offset_x)
            print("offset y ", type(self.image_offset_y), self.image_offset_y)
            _, = ky.KYFG_SetCameraValueInt(self.cam_handle_array[self.grabber_index][0], 'OffsetX', self.image_offset_x)
            _, = ky.KYFG_SetCameraValueInt(self.cam_handle_array[self.grabber_index][0], 'OffsetY', self.image_offset_y)
            _, = ky.KYFG_SetCameraValueInt(self.cam_handle_array[self.grabber_index][0], "Width", self.image_width)
            _, = ky.KYFG_SetCameraValueInt(self.cam_handle_array[self.grabber_index][0], "Height", self.image_height)
            

    def _allocate_memory(self):
        _, payload_size, _, _ = ky.KYFG_StreamGetInfo(self.camera_stream_handle, ky.KY_STREAM_INFO_CMD.KY_STREAM_INFO_PAYLOAD_SIZE)

        _, buf_allignment, _, _ = ky.KYFG_StreamGetInfo(self.camera_stream_handle, ky.KY_STREAM_INFO_CMD.KY_STREAM_INFO_BUF_ALIGNMENT)

        for iFrame in range(len(self.stream_buffer_handle)):
            self.stream_alligned_buffer[iFrame] = ky.aligned_array(buf_allignment, ky.c_ubyte, payload_size)
            _, self.stream_buffer_handle[iFrame] = ky.KYFG_BufferAnnounce(self.camera_stream_handle, self.stream_alligned_buffer[iFrame], None)


    def _stream_callback_func(self, buff_handle, user_context):

        #print("hola")
        ti = time()

        if buff_handle == 0:
            self._stream_callback_func.__func__.copyingDataFlag = 0
            return
        #print(buff_handle)


        _, self._time_stamp, _, _ =  ky.KYFG_BufferGetInfo(buff_handle, ky.KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_TIMESTAMP)

        stream_info = ky.cast(user_context, ky.py_object).value
        stream_info.callbackCount = stream_info.callbackCount + 1

        _, pointer, _, _ = ky.KYFG_BufferGetInfo(buff_handle, ky.KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_BASE)
        _, buffer_size, _, _ = ky.KYFG_BufferGetInfo(buff_handle, ky.KY_STREAM_BUFFER_INFO_CMD.KY_STREAM_BUFFER_INFO_SIZE)

        buffer_byte_array = bytearray(ctypes.string_at(pointer, buffer_size))
        data = np.frombuffer(buffer_byte_array, dtype=np.uint16)
        #self.image = data.reshape(self.image_height, self.image_width)
        self.queue.put(data.reshape(self.image_height, self.image_width))
        #print("QUEUE CALLBACK", len(self.queue.queue))
        tf = time()
        #print(tf-ti)


        if self._stream_callback_func.__func__.copyingDataFlag == 0:
           self._stream_callback_func.__func__.copyingDataFlag = 1

        sys.stdout.flush()
        self._stream_callback_func.__func__.copyingDataFlag = 0
        return 

    def _start_camera(self, n_frames):
        # put all buffers to input queue
        KYFG_BufferQueueAll_status, = ky.KYFG_BufferQueueAll(self.camera_stream_handle, ky.KY_ACQ_QUEUE_TYPE.KY_ACQ_QUEUE_UNQUEUED, ky.KY_ACQ_QUEUE_TYPE.KY_ACQ_QUEUE_INPUT)
        
        KYFG_CameraStart_status, = ky.KYFG_CameraStart(self.cam_handle_array[self.grabber_index][self.camera_index], self.camera_stream_handle, n_frames)
        return 0

    def set_gain_exposure(self, gain, exposure_time):
        print("EXP TIME ", exposure_time)
        exposure_time = round(float(exposure_time), 0)
        #gain = round(float(gain)/100, 0) comento para probar cosas acá
        _,  = ky.KYFG_SetCameraValue(self.cam_handle_array[self.grabber_index][0], "ExposureTime", exposure_time)
        _, self.exposure_time =  ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "ExposureTime")
        _,  = ky.KYFG_SetCameraValue(self.cam_handle_array[self.grabber_index][0], "Gain", gain)
        _, self.gain =  ky.KYFG_GetCameraValue(self.cam_handle_array[self.grabber_index][0], "Gain")
        
        return

    def get_frame(self, n_frames=1):
        
        sys.stdout.flush()


        self._start_camera(n_frames)

#        self.image_array = []
#        for index in range(n_frames):
        ##print("QUEUE ANTES", len(self.queue.queue))
        self.image = self.queue.get()
        #print("QUEUE DESPUES", len(self.queue.queue))
        #self.queue.queue.clear()
        #    self.image_array.append(self.image)

        self._stream_callback_func.__func__.copyingDataFlag = 1
        sys.stdout.flush()
        _, = ky.KYFG_CameraStop(self.cam_handle_array[self.grabber_index][0])
        

        return self.image
    
    def __del__(self):
        self.close()

    def close(self):
        if self._is_camera_open:
            chandle = self.cam_handle_array[self.grabber_index][0]
            print("------")
            print(self.cam_handle_array)
            print(chandle)
            print(type(chandle))
            _, = ky.KYFG_CameraClose(self.cam_handle_array[self.grabber_index][0])
            _, = ky.KYFG_Close(self.handle[self.grabber_index])
            self._is_camera_open = False

    class StreamInfoStruct:
        def __init__(self):
            self.width = 640
            self.height = 480
            self.callbackCount = 0
            return

#IMPORTANTE: el offset en x va en múltiplos de 32 y el offset de y va en múltiplos de 2
roi_nuestro = ((0,0), (9344, 7000))

def tomar2(imperx, tiempo_exp):
    imperx.set_gain_exposure(1.25, int(round(tiempo_exp, 1)))
    sleep(0.05)
    imagenes = np.zeros(shape = (2, 7000,9344))
    means = []
    for i in range(2):
        imagen = imperx.get_frame(2)
        imperx.queue.queue.clear()
        imagenes[i] = imagen
        means.append(np.mean(imagen)) 
    
    var = np.var(imagenes[0]- imagenes[1])/(2)
    resta_means = means[0] - means[1]
    return var, resta_means

def mean_movil(imperx, tiempo_exp, rep):
    imperx.set_gain_exposure(1.25, int(round(tiempo_exp, 1)))
    sleep(0.05)
    img_mean = np.zeros(shape=(7000, 9344))
    img_var  = np.zeros(shape = (7000,9344))
    xcuad = np.zeros(shape = (7000, 9344))
    for i in range(rep):
        print(i)
        im = imperx.get_frame(2)
        imperx.queue.queue.clear()
        img_mean = img_mean + im/rep
        xcuad = xcuad + np.multiply(im,im)/rep
        img_var = xcuad - np.multiply(img_mean,img_mean)
    return img_mean, img_var


def toma1(imperx, tiempo_exp):
    imperx.set_gain_exposure(1.25, int(round(tiempo_exp, 1)))
    sleep(0.05)
    imagenes = np.zeros(shape = (2, 7000,9344))
    imagen = imperx.get_frame(2)
    imperx.queue.queue.clear()
    mean = np.mean(imagen)
    
    var = np.var(imagen)

    return var, mean

def guardar_imagenes(imperx, n_frames, ganancia, tiempos_de_exposicion, ROOT):
    for tiempo in tiempos_de_exposicion:
        # Ajustar la ganancia y la exposición
        imperx.set_gain_exposure(ganancia, int(round(tiempo, 1)))
        
        # Capturar las imágenes para el tiempo de exposición actual
        imagenes = imperx.obtener_imagenes(n_frames)

        # Crear la carpeta correspondiente al tiempo de exposición en milisegundos
        nombre_carpeta = f"{int(tiempo)}ms"
        ruta_carpeta = os.path.join(ROOT, nombre_carpeta)
        
        # Verificar si la carpeta existe, y si no, crearla
        if not os.path.exists(ruta_carpeta):
            os.makedirs(ruta_carpeta)

        # Guardar cada imagen en la carpeta correspondiente
        for i, imagen in enumerate(imagenes):
            ruta_archivo = os.path.join(ruta_carpeta, f"imagen_frame_{i+1}.tiff")
            tiff.imwrite(ruta_archivo, imagen.astype(np.float32))
    return print("Imágenes guardadas")

    

def obtener_imagenes(self, n_frames):
    sys.stdout.flush()

    # Iniciar la cámara con el número de frames deseado
    self._start_camera(n_frames)

    # Lista para almacenar los frames si se capturan múltiples
    image_array = []
    
    for index in range(n_frames):
        # Capturar cada frame de la cola
        image = self.queue.get()
        image_array.append(image)
    
    # Marca que los datos están siendo copiados
    self._stream_callback_func.__func__.copyingDataFlag = 1
    sys.stdout.flush()

    # Detener la cámara una vez se hayan capturado los frames
    _, = ky.KYFG_CameraStop(self.cam_handle_array[self.grabber_index][0])

    # Devolver la lista de frames o el único frame capturado
    if n_frames == 1:
        return image_array[0]
    else:
        return image_array

