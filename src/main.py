
import h5py
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os
from matplotlib import animation

from src.preprocessing import dataset
from src.correlation import correlation_mapping

class params:
    def __init__(self, data_type):
        self.data_type = data_type
        self.data_directory = os.path.join(os.getcwd(),'data','raw', self.data_type)        # data directory
        self.save_directory = os.path.join(os.getcwd(),'data','processed', self.data_type)  # save directory
        self.AcqInfo = 'AcqInfo.mat'                                                        # acquisition parameters
        self.save_videos = False                                                            # save generated videos
        self.save_correlation = False                                                       # save correlation map
        self.baseline_frames = 10                                                           # number of frames for baseline CBV calc
        self.wn = 4                                                                         # window size for RF moving temporal average
        self.filter_CBV = True                                                              # apply median filter to CBV
        self.filt_size = 3                                                                  # median filter size [CBV and correlation]
        self.stimulation_length = 10                                                        # stimulation template duration
        self.stimulation_start = 20                                                         # stimulation template start
        self.threshold = 0.23                                                               # correlation threshold
    def initialize(self):
        if not os.path.exists(self.save_directory):
            os.mkdir(self.save_directory)
        # adjust plot parameters for whole session
        plt.rcParams['image.cmap'] = 'afmhot'
        plt.rcParams['pdf.fonttype'] = 42
        plt.rcParams['ps.fonttype'] = 42
        new_rc_params = {'text.usetex': False,"svg.fonttype": 'none'}
        plt.rcParams.update(new_rc_params)
        # generate transparent map for CBV
        cmap = plt.cm.RdBu
        self.cmap = cmap(np.arange(cmap.N))
        self.cmap[:,-1] = np.abs(np.linspace(-1, 1, cmap.N))**2
        self.cmap = matplotlib.colors.ListedColormap(self.cmap)
        # generate transparent map for correlation
        cmap = plt.cm.gist_heat
        self.cmap2 = cmap(np.arange(cmap.N))
        self.cmap2[:,-1] = np.abs(np.linspace(0, 1, cmap.N))**2
        self.cmap2 = matplotlib.colors.ListedColormap(self.cmap2)

# ----- initialize parameters ------- #
P = params('electric_stimulation')
P.initialize()

# ----- generate dataset ------- #
DS = dataset.dataset(P)

# plot arguments
scale1 = {'vmin':0, 'vmax': 0.05, 'cmap':'gray','extent':P.im_extent,'aspect':'auto', 'origin':'lower'}
scale2 = {'vmin':-100, 'vmax': 100, 'alpha':1,'cmap':P.cmap,'extent':P.im_extent,'aspect':'auto', 'origin':'lower'}

# view RF video
DS.visualize(P,'RF',scale1)

# calculate CBV
DS.generate_CBV(P)

# view CBV video
DS.visualize(P,'CBV',scale1,scale2)

# ----- generate correlation map ------- #
CORR = correlation_mapping.correlate()

# plot arguments
scale1 = {'vmin':0, 'vmax': 0.05, 'cmap':'gray','extent':P.im_extent,'aspect':'auto', 'origin':'lower'}
scale2 = {'vmin':P.threshold, 'vmax': 1, 'alpha':1,'cmap':P.cmap2,'extent':P.im_extent,'aspect':'auto', 'origin':'lower'}

# calculate Pearson correlation
CORR.map_corr(DS,P)

# plot correlation map
CORR.visualize(DS,P,scale1,scale2)
