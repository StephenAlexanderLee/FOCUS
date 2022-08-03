from numba import jit
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

class correlate:
    def __init__(self):
        self.id = 0
    def map_corr(self,data,params):
        map = np.zeros(params.imgsize)
        for v in range(params.imgsize[0]):
            for w in range(params.imgsize[1]):
                map[v,w] = calc_r(data.RF,data.template,v,w)
        map[map < params.threshold] = 0
        self.map = signal.medfilt2d(map,params.filt_size)
    def visualize(self,data,params,scale1,scale2):
        fig , ax = plt.subplots(1,1,figsize=(10,5))
        im = ax.imshow(data.RF[:,:,0],**scale1)
        im = ax.imshow(self.map,**scale2)
        ax.set_xlim((-4.5,4.5))
        ax.set_ylim(params.im_extent[3],params.im_extent[2])
        ax.set_xlabel('mm',fontsize=16)
        ax.set_ylabel('mm',fontsize=16)
        cbar = fig.colorbar(im, ax = ax, fraction = 0.025, pad = 0.01)
        cbar.ax.set_ylabel('Correlation', rotation = 270, labelpad = 10)
        plt.show()

@jit(nopython = True)
def calc_r(s,A,v,w):
    r = 0
    r1 = r; r2 = r; r3 = r
    for i in range(len(A)):
        r1 += (s[v,w,i]-np.mean(s[v,w,:]))*(A[i]-np.mean(A))
        r2 += (s[v,w,i]-np.mean(s[v,w,:]))**2
        r3 += (A[i]-np.mean(A))**2
    r = r1/(np.sqrt(r2)*np.sqrt(r3))
    return r
