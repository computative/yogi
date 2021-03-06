from slaterkoster.slaterkoster import Slaterkoster as sk
import numpy as np
from basisIter import Basis
from numpy import array as ar
import sys
import utils

class Hamiltonian:

    def __init__(self, crystal, functions, params):
        # init

        self.crystal = crystal

        # find W by transforming cubic coords
        a1,a2,a3 = self.crystal.lattice
        A = np.array([a1,a2,a3]).T

        neighbors = 1
        self.neighbors=[]

        for i in range(-neighbors, neighbors+1):
            for j in range(-neighbors, neighbors+1):
                for k in range(-neighbors, neighbors+1):
                    self.neighbors.append(  np.dot(A, ar([ i, j, k]) ) )

        basis = Basis(crystal, functions)
        self.sk = sk(basis, params, self.neighbors)

        self.N = len(basis)

        self.HGamma = self.sk.HGamma()



    def __call__(self, k):
        N = self.N
        H = np.zeros( (N,N) , dtype=complex )
        for i, G in enumerate(self.neighbors):          
            H += np.exp(1j*np.dot( G, k ))*self.HGamma[i]
        return H

    @staticmethod
    def isHermitian(H, eps = 1e-6):
        n1 = len(H[:,0])
        n2 = len(H[0,:])
        for i in range( n1 ):
            for j in range(i+1, n2 ):
                if np.abs( H[i,j] - (H.T.conj())[i,j] ) > eps:
                    print( "Non-Hermitian at idx (i,j) = " + str( (i,j) )\
                        + "with values for H[i,j] = " + str(H[i,j]) \
                        + " and H[i,j].T.conj() = " + str((H.T.conj())[i,j]))
        return True



if __name__ == "__main__":
    from crystal import Crystal

    crl = Crystal(dims=(1,1,1)).from_struct(
        {"type": "diamond", "spp": ["Si","Si"]}
    )
    bowler = {  "Es": -12.2, "Ep": -5.75, 
                "ss-sigma": -1.938, "sp-sigma": 1.745,
                "pp-sigma": 3.050, "pp-pi": -1.075 }



    hamiltonian = Hamiltonian(crl, ["1s","2px","2py","2pz"], bowler)

    eigs = []



    from visualtools import VisualTools
    sympts = VisualTools.fcc_sympts(crl.lat_const(1))
    kpath = {
        "waypts": [ sympts["K"], sympts["Gamma"],sympts["L"], sympts["K"]  ],
        "n" : [35,35,35]
    }


    for i, k in enumerate(VisualTools.kpts(kpath["waypts"], kpath["n"])):
        print( "Iteration", i )
        HMatrix = hamiltonian( k )

        if np.linalg.norm(k) == 0:
            VisualTools.matrix_formatting()
            print( np.round( HMatrix,3 ))
        if not Hamiltonian.isHermitian(HMatrix):
            raise(ValueError("Hamiltonian nonhermitian"))
        eigs.append(np.linalg.eigvalsh( HMatrix, "L"))

    bands = np.array(eigs).T
    VisualTools.bands(bands)

