# TMELand
TMELand is a software tool for modeling and visualization of Waddington's epigenetic landscape and state transition paths based on dynamical models of gene regulatory network (GRN).

Our paper on TMELand has been submitted:  
[Lin Zhu, Xin Kang, Pei Lin, Chunhe Li and Jie Zheng. TMELand: Quantitative modeling and visualization of Waddington’s epigenetic landscape and state transition paths[J], 2021.]    
For more details, please check out the [User Manual](https://github.com/JieZheng-ShanghaiTech/TMELand/blob/main/TMELand%20Manual.pdf).




### Installation
TMELand is developed by Python, you can install `python==3.7` or install [Anaconda](https://docs.anaconda.com/anaconda/install/) and create virtual environment.

```
# (Only needed for conda) create virtual environment and activate it
$ conda create –n TMELand_env python==3.7
$ conda activate TMELand_env

# Install packages using requirements.txt file in the current path
$ pip install -r requirements.txt
```



### Launch

You can launch TMELand in the terminal after finish installation.

For Windows:
```
$ python ./MainPage.py
```

For Ubuntu:

```
$ python ./MainPage.py
```

For macOS:

```
$ python ./MainPageForMac.py
```



### Usages
#### Input: 
The TMELand supports TSV, ODE, SBML, and TME files.

* TSV: TSV (Tab-separated values) stores the interaction relationship among nodes in gene regulatory network, activation is `+`, inhibition is `-`. Please refer to a file in the `./TSV_models/` directory to find an example.

* ODE: ODE (XPPAUT ODE) refers to the `.ode` format, which is a set of ODE equations. Please refer to the `./ODE_SBML_models/` directory to find an example.

* SBML: You can also provide your self-defined ODE functions in SBML format. TMELand supports SBML models come from the BioModels website.

* TME: TME is a self-defined format to save computed models. After you construct a landscape or a landscape with paths, you can save it as a TME model for the next reloading.

#### Main functions:
* Model visualization

After loading your models, you can obtain the parsed and visualized results of your models.
* Drawing landscape

To draw a landscape, there are three steps:
1. **Form ODE equations** (only needed for TSV models): by `Dynamics setting` button to generate ODE equations.

2. **Draw**: this step corresponding to the `Draw` button, which includes simulation and default visualization (using the first two marker genes and setting visualization range from 0 to 3).

3. **Update**: you can adjust the marker genes and range to update the landscape by `Update` button. If you need to change model-related parameters, you only need to click `Draw` button without reupdate. Furthermore, update is also worked for a TME model, you can update the landscape shape after load a TME model.

* Drawing transition paths

After drawing the landscape, you can draw state transition paths between two attractors by specifying time range, granularity, beginning and ending attractors. You can also draw paths after load a TME model, and update landscape will keep paths.



#### Summary

Here's a summary pipeline:

![](./resource/Quick_tutorial.jpg)

For more details, please refer to the [User Manual](https://github.com/JieZheng-ShanghaiTech/TMELand/blob/main/TMELand%20Manual.pdf).