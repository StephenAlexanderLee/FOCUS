import os
import h5py
import numpy as np
from natsort import natsorted
import matplotlib.pyplot as plt
from matplotlib import animation
from scipy import signal

class dataset:
    def __init__(self, params):
        self.data_directory = os.path.join(params.data_directory,'Acquisitions')
        self.files = natsorted(os.listdir(self.data_directory))
        AcqInfo = os.path.join(params.data_directory,params.AcqInfo)
        for u, v in h5py.File(AcqInfo, mode = 'r').items():
            try:
                exec("params.%s = v" % u)
            except:
                pass
        params.im_extent = [params.CUDArecon['imXrange'][0][0],params.CUDArecon['imXrange'][-1][0],
            params.CUDArecon['imZrange'][0][0], params.CUDArecon['imZrange'][-1][0]]
        params.im_extent = [x*params.Trans['wl'][0][0]*1e3 for x in params.im_extent]
        params.imgsize = [int(params.CUDArecon['imZsize'][0]),int(params.CUDArecon['imXsize'][0])]
        params.frames = int(len(self.files))
        self.generate_template(params)
        rcvdata = np.zeros((params.imgsize[0],params.imgsize[1],len(self.files)))
        for i, f in enumerate(self.files):
            filepath = os.path.join(self.data_directory,f)
            for u, v in h5py.File(filepath, mode = 'r').items():
                rcvdata[:,:,i] = np.transpose(np.array(v))
            print('.',end='',flush=True)
        print()
        rcvdata = rcvdata/np.max(rcvdata)
        params.frames = params.frames-(params.wn-1)
        self.RF = np.zeros([params.imgsize[0],params.imgsize[1],params.frames])
        for z in range(params.imgsize[0]):
            for x in range(params.imgsize[1]):
                self.RF[z,x,:] = self.moving_average(rcvdata[z,x,:],params.wn)
    def generate_template(self,params):
        self.template = np.zeros(params.frames)
        self.template[params.stimulation_start:params.stimulation_start+params.stimulation_length]=1
        self.template = self.moving_average(self.template,params.wn)
        self.template[self.template>0] = 1
    def moving_average(self, x, wn = 4):
        return np.convolve(x,np.ones(wn),'valid') / wn
    def visualize(self, params, type, imgarg1 = None, imgarg2 = None):
        fig, ax = plt.subplots(1,1,figsize=(10,5))
        ax.set_xlim((-4.5,4.5))
        ax.set_ylim(params.im_extent[3],params.im_extent[2])
        ax.set_xlabel('mm',fontsize=16)
        ax.set_ylabel('mm',fontsize=16)
        if type == 'RF':
            def init():
                im1.set_data(self.RF[:,:,0])
                return im1
            def animate(j):
                im1.set_array(self.RF[:,:,j])
                return im1
            im1 = ax.imshow(self.RF[:,:,0],**imgarg1)
        if type == 'CBV':
            def init():
                im1.set_data(self.RF[:,:,0])
                im2.set_data(self.CBV[:,:,0])
                return im1, im2
            def animate(j):
                im1.set_array(self.RF[:,:,j])
                im2.set_array(self.CBV[:,:,j])
                return im1, im2
            im1 = ax.imshow(self.RF[:,:,0],**imgarg1)
            im2 = ax.imshow(self.CBV[:,:,0],**imgarg2)
            cbar = fig.colorbar(im2, ax = ax, fraction = 0.025, pad = 0.01)
            cbar.ax.set_ylabel(r'$\Delta$ CBV/CBV', rotation = 270, labelpad = 10)
        ani = animation.FuncAnimation(fig, animate, frames=range(params.frames), init_func=init, repeat=True)
        if params.save_videos:
            ani.save(filename=os.path.join(params.save_directory,type+'_movie.mp4'))
            writergif = animation.PillowWriter(fps=30)
            ani.save(filename=os.path.join(params.save_directory,type+'_movie.gif'), writer=writergif)
        plt.show()
    def filter_CBV(self,params):
        for i in range(params.frames):
            self.CBV[:,:,i] = signal.medfilt2d(self.CBV[:,:,i],params.filt_size)
    def generate_CBV(self,params):
        self.CBV = np.zeros(self.RF.shape)
        baseline = np.mean(self.RF[:,:,:params.baseline_frames],axis=-1)
        for i in range(params.frames):
            self.CBV[:,:,i] = (self.RF[:,:,i]-baseline)/baseline*100
        if params.filter_CBV:
            self.filter_CBV(params)
