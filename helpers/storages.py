import abc
import os

from globals import PRIVATE_STORAGE_PATH

class FileStorage(abc.ABC):
    
    @abc.abstractmethod
    def read(self, name):
        pass
    
    @abc.abstractmethod
    def save(self, file, name):
        pass
    
    @abc.abstractmethod
    def remove(self, name) -> bool:
        pass
    
    def update(self, file, name) -> bool:
        
        if not self.exists(name): return False
        
        self.remove(name)
        self.save(file, name)
        
        return True
        
    
    def removeAllFiles(self, *names) -> bool:
        
        allOk = True
        
        if len(names) == 0:
            names = os.listdir(self.path)
        
        for name in names:
            if not self.remove(name):
                allOk = False
            
        return allOk
    
    @abc.abstractmethod
    def removeAll(self):
        pass
    
    @abc.abstractmethod
    def exists(self, name) -> bool:
        pass
    
class PrivateStorage(FileStorage):
    def __init__(self, path = PRIVATE_STORAGE_PATH):
        self.path = path
        
        if not os.path.exists(self.path):
            os.makedirs(self.path)
        
    def read(self, name, mode = 'r'):
        if self.exists(name):
            return open(os.path.join(self.path, name), mode)
        else:
            return None
    
    def save(self, file, name, mode = 'w'):
        with open(os.path.join(self.path, name), mode) as f:
            f.write(file.read())
    
    def write(self, content, name, mode = 'w'):
        with open(os.path.join(self.path, name), mode) as f:
            f.write(content)
            
        return self.exists(name)
    
    def remove(self, name) -> bool:
        if self.exists(name):
            os.remove(os.path.join(self.path, name))
            return True
        
        return False
    
    def removeAll(self):
        os.remove(self.path)
    
    def exists(self, name) -> bool:
        return os.path.exists(os.path.join(self.path, name))

    
def pdfFile(fun):
    
    def wrapper(self, name, *args, **kwargs):
        return fun(self, str(name) + '.pdf', *args, **kwargs)
    
    return wrapper
    
    
