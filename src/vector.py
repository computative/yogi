import numpy as np

class c(np.ndarray):
    def __new__(cls, *args):
        return np.array(args)

    def __eq__(self,x,y):
        if np.linalg.norm(x-y) < self.eps:
            return True
        return False