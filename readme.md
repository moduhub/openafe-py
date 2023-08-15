

# OpenAFE Plotter PY Version
This script talks to a device running [OpenAFE Comm](), giving the device the necessary commands to make following voltammetry processes: cyclic, differential pulse and square wave.

> NOTE: The DPV and SWV processes are not yet implemented.

![plotterexample](https://github.com/ig-66/OpenAFE_PythonPlotter/blob/main/images/openafeplotter.png)

# External Requirements
- An Arduino Uno running [OpenAFE Comm]().
- An OpenAFE Shield.

# How to Use

## If You Don't Have Python Installed
* Install python (64 bits) in your machine, it is available on this [link](https://www.python.org/downloads/)
> It is important that the python version installed is 64 bits, because otherwise the `matplotlib` may fail to install.

## If You Already Have Python Installed

* Install [matplotlib](https://matplotlib.org/stable/index.html) with pip through your machine terminal (cmd/bash):
```
pip install matplotlib
```
* Download, clone or copy the `openafe_plotter.py` script into a folder of your preference.

* Then, open the `openafe_plotter.py` file, and modify the parameters present on the top of the script:
```py
# Adjust the parameters below according to your needs:
# Comment or de-comment the voltammetry type as needed.
# Parameters:
voltammetryType = "CV" # Cyclic Voltammetry
# voltammetryType = "DPV" # Differential Pulse Voltammetry
# voltammetryType = "SW" # Square Wave
startingPotential_millivolts = -500
endingPotential_millivolts = 500
scanRate_millivoltsPerSecond = 250
stepSize_millivolts = 2
numberOfCycles = 1
settlingTime_milliseconds = 1000

# Graph Options:
graphTitle = "H2O + NaCl Cyclic Voltammetry" # the graph title to be displayed, can be left in blank
graphSubTitle = "" # the graph sub title, can be left blank
gridVisible = True # Change to True or False, to make the grid visible or hidden, respectively
```

* After that, symply run it, with the following command:
```
python openafe_plotter.py
```

That's it! Once the graph is done you can tweak it to your liking and then save it, if you wish.
