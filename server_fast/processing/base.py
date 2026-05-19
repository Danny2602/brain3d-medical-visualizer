from abc import ABC, abstractmethod

import numpy as np
#Clase base para los filtros de procesamiento de imagen, se define un método abstracto "apply" que debe ser implementado por las clases hijas. Este método toma una imagen en formato de matriz numpy y un diccionario opcional de historial, y devuelve la imagen procesada también en formato de matriz numpy.
class BaseFilter(ABC):
    @abstractmethod
    def apply(self, img: np.ndarray,history: dict = None, **kwargs)-> np.ndarray:
        pass