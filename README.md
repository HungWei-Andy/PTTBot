# ICBT2017: PTTBot2
The project of NTU ICBT2017

# PyMDNet
* [Requirements](#requirements)
* [Usage](#usage)


## Requirements
### Download
Please download packages by executing download.sh before running the code:
```bash
  bash download.sh
```

### Python Requirements
The python version is Python 2.7.
The required library is listed below and in requirements.txt
```bash
gym>=0.9.1
keras-rl
tensorflow>=1.0.0
keras>=2.0.2
h5py>=2.6.0
pandas>=0.13.1
```

### Keras Theano Backend
Please turn the backend of keras into theano backend. [[reference1]](https://stackoverflow.com/questions/42177658/how-to-switch-backend-with-keras-from-tensionflow-to-theano)[[reference2]](https://keras.io/backend/)

## Usage
### Run the server
```bash
  python runserver.py
```

### Reinforcement Learning of Dialogue Policy
```bash
  python agent_pttbot.py
```

