import abc
import os

from globals import PRIVATE_STORAGE_PATH

class FileStorage(abc.ABC):
    """
    Interfaz abstracta para el almacenamiento de archivos.
    """
    @abc.abstractmethod
    def read(self, name):
        """Lee el contenido de un archivo."""
        pass
    
    @abc.abstractmethod
    def save(self, file, name):
        """Guarda el contenido en un archivo."""
        pass
    
    @abc.abstractmethod
    def remove(self, name) -> bool:
        """Elimina un archivo."""
        pass
    
    def update(self, file, name) -> bool:
        """
        Actualiza el contenido de un archivo.

        :param file: Nuevo contenido del archivo.
        :param name: Nombre del archivo a actualizar.
        :return: True si la actualización fue exitosa, False si el archivo no existe.
        """
        if not self.exists(name):
            return False
        
        self.remove(name)
        self.save(file, name)
        
        return True
        
    
    def removeAllFiles(self, *names) -> bool:
        """
        Elimina varios archivos.

        :param names: Nombres de los archivos a eliminar.
        :return: True si la eliminación fue exitosa para todos los archivos, False si al menos uno no pudo ser eliminado.
        """
        allOk = True
        
        if len(names) == 0:
            names = os.listdir(self.path)
        
        for name in names:
            if not self.remove(name):
                allOk = False
            
        return allOk
    
    @abc.abstractmethod
    def removeAll(self):
        """Elimina todos los archivos."""
        pass
    
    @abc.abstractmethod
    def exists(self, name) -> bool:
        """Verifica si un archivo existe."""
        pass
    
class PrivateStorage(FileStorage):
<<<<<<< Updated upstream
    def __init__(self, path = PRIVATE_STORAGE_PATH):
        self.path = path
=======
    """
    Implementación de FileStorage para almacenamiento privado.
    """
    def __init__(self):
        """
        Inicializa el almacenamiento privado.
        """
        self.path = PRIVATE_STORAGE_PATH
>>>>>>> Stashed changes
        
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        
    def read(self, name, mode='r'):
        """
        Lee el contenido de un archivo.

        :param name: Nombre del archivo a leer.
        :param mode: Modo de apertura del archivo (por defecto: 'r' para lectura).
        :return: Contenido del archivo o None si el archivo no existe.
        """
        if self.exists(name):
            return open(os.path.join(self.path, name), mode)
        else:
            return None
    
    def save(self, file, name, mode='w'):
        """
        Guarda el contenido en un archivo.

        :param file: Contenido a guardar en el archivo.
        :param name: Nombre del archivo.
        :param mode: Modo de apertura del archivo (por defecto: 'w' para escritura).
        """
        with open(os.path.join(self.path, name), mode) as f:
            f.write(file.read())
    
    def write(self, content, name, mode='w'):
        """
        Escribe el contenido en un archivo.

        :param content: Contenido a escribir en el archivo.
        :param name: Nombre del archivo.
        :param mode: Modo de apertura del archivo (por defecto: 'w' para escritura).
        :return: True si la escritura fue exitosa, False si el archivo no existe.
        """
        with open(os.path.join(self.path, name), mode) as f:
            f.write(content)
            
        return self.exists(name)
    
    def remove(self, name) -> bool:
        """
        Elimina un archivo.

        :param name: Nombre del archivo a eliminar.
        :return: True si la eliminación fue exitosa, False si el archivo no existe.
        """
        if self.exists(name):
            os.remove(os.path.join(self.path, name))
            return True
        
        return False
    
    def removeAll(self):
        """Elimina todos los archivos en el almacenamiento privado."""
        for filename in os.listdir(self.path):
            file_path = os.path.join(self.path, filename)
            os.remove(file_path)
    
    def exists(self, name) -> bool:
        """
        Verifica si un archivo existe.

        :param name: Nombre del archivo.
        :return: True si el archivo existe, False si no.
        """
        return os.path.exists(os.path.join(self.path, name))

def pdfFile(fun):
    """
    Decorador que agrega la extensión '.pdf' al nombre del archivo.

    :param fun: Función a decorar.
    :return: Función decorada.
    """
    def wrapper(self, name, *args, **kwargs):
        return fun(self, str(name) + '.pdf', *args, **kwargs)
    
    return wrapper
