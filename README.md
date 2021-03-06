# leaf
A very simple command-line utility to control and view data from your Nissan Leaf, using Python.

![example](https://github.com/willemcvu/leaf/blob/master/example.png)


## Usage
1. Clone to a convenient location, and add that directory to your path.
2. Install https://github.com/nricklin/leafpy: `$ pip install leafpy`
3. Add your NissanConnect username and password to config.ini
4. Control your climate control system and view battery and energy info!

```
$ leaf -h
usage: leaf [-h] {climateon,climateoff,batteryinfo,energyinfo} ...

positional arguments:
  {climateon,climateoff,batteryinfo,energyinfo}

optional arguments:
  -h, --help            show this help message and exit
```
