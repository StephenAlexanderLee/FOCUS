# FOCUS (fUS-imaging)
## Functional Observation of the Cortex via UltraSound
functional ultrasound (fUS) analysis pipeline for visualizing cerebral blood volume (CBV) changes and correlation. Starter code is included (main.py) and described below.

## Setup
### 1. Install Requirements
1. Python 3.8.0
2. h5py==2.10.0,
  numpy==1.18.5,
  scipy==1.4.1,
  natsort==7.0.1,
  matplotlib==3.3.2,
  numba==0.51.2

### 2. Installation
1. download the distribution file (focus*.whl)
2. install using pip
```python
python -m pip install focus*.whl
```

## Changes in hemodynamics as indicators of brain activation

<br>

<img src="https://github.com/StephenAlexanderLee/fUS-imaging/blob/main/media/CBV_movie.gif" width="75%" />

## Correlation map
correlation is calculated as the pixel-by-pixel Pearson correlation with the stimulation signal template.

<br>

<img src="https://github.com/StephenAlexanderLee/fUS-imaging/blob/main/media/correlation.svg" width="75%" />



## Starting Code
### import the required modules (preprocessing and correlation are custom)
```python
import h5py
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import os
from matplotlib import animation

from src.preprocessing import dataset
from src.correlation import correlation_mapping
```

### Initialize custom parameters and workspace
Parameters within the params class can be altered. Enter your data directory "<insert-data-path-here>" and save directory to "<inter-save-path-here>".
<br>

```python
class params:
    def __init__(self, data_type):
        self.data_type = data_type
        self.data_directory = <insert-data-path-here> # data directory
        self.save_directory = <insert-save-path-here> # save directory
        self.AcqInfo = 'AcqInfo.mat'                  # acquisition parameters
        self.save_videos = False                      # save generated videos
        self.baseline_frames = 10                     # number of frames for baseline CBV calc
        self.wn = 4                                   # window size for RF moving temporal average
        self.filter_CBV = True                        # apply median filter to CBV
        self.filt_size = 3                            # median filter size [CBV and correlation]
        self.stimulation_length = 10                  # stimulation template duration
        self.stimulation_start = 20                   # stimulation template start
        self.threshold = 0.23                         # correlation threshold
    def initialize(self):
        # adjust plot parameters for whole session
        plt.rcParams['image.cmap'] = 'afmhot'
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps = 60, metadata = dict(artist='Me'), bitrate = 1800)
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
```

### Generate the dataset and visualize the raw data
```python
# ----- generate dataset ------- #
DS = dataset.dataset(P)

# plot arguments
scale1 = {'vmin':0, 'vmax': 0.05, 'cmap':'gray','extent':P.im_extent,'aspect':'auto', 'origin':'lower'}
scale2 = {'vmin':-100, 'vmax': 100, 'alpha':1,'cmap':P.cmap,'extent':P.im_extent,'aspect':'auto', 'origin':'lower'}

# view RF video
DS.visualize(P,'RF',scale1)
```

### Generate CBV changes
```python
# calculate CBV
DS.generate_CBV(P)

# view CBV video
DS.visualize(P,'CBV',scale1,scale2)
```

### Calculate correlation maps
```python
# ----- generate correlation map ------- #
CORR = correlation_mapping.correlate()

# plot arguments
scale1 = {'vmin':0, 'vmax': 0.05, 'cmap':'gray','extent':P.im_extent,'aspect':'auto', 'origin':'lower'}
scale2 = {'vmin':P.threshold, 'vmax': 1, 'alpha':1,'cmap':P.cmap2,'extent':P.im_extent,'aspect':'auto', 'origin':'lower'}

# calculate Pearson correlation
CORR.map_corr(DS,P)

# plot correlation map
CORR.visualize(DS,P,scale1,scale2)
```

<!-- CONTACT -->
## Author

Stephen Alexander Lee - [@stephenalexlee](https://twitter.com/stephenalexlee) - stephen.alexander.lee@gmail.com

Project Link: [https://github.com/StephenAlexanderLee/fUS-imaging](https://github.com/StephenAlexanderLee/fUS-imaging)

<p align="right">(<a href="#top">back to top</a>)</p>
