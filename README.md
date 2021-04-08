# TMELand
A software tool for modeling and visualization of Waddington's epigenetic landscape based on dynamical models of gene regulatory network (GRN).

Our paper has been submitted, you can refer to [User Manual](https://github.com/JieZheng-ShanghaiTech/TMELand/blob/main/TMELand%20Manual.pdf) for more details.

----
### Installation
#### conda
We recommand using [Conda](https://conda.io/docs/) to create virtual environment and then install packages. However, you can also use pip to install necessary packages directly.

```
$ conda create –n TMELand_env python==3.7    
$ conda activate TMELand_env    
$ pip install -r requirements.txt    
```
----
### Launch
For Windows and Ubuntu OS
```
$ python ./MainPage.py
```

For macOS:

```
$ python ./ MainPageForMac.py
```
----
### Usages
#### Input: 
The TMELand supports TSV, ODE, SBML, and TME files.
**TSV**: TSV (Tab-separated values) stores the interaction relationship among nodes in gene regulatory network, activation is +, inhibition is -. Please refer to a file in the `./TSV_models/` to find an example.
**ODE**: ODE (XPPAUT ODE) refers to .ode format, which is a set of ODE equations. Please refer to the `./ODE_SBML_models/` to find an example.
**SBML**: You can also provide your self-define ODE functions by SBML format. TMELand supports SBML models come from BioModels website.
**TME**: TME is a self-define format to save computed model. After you construct landscape only or landscape with paths, you can save it as a TME model for next reloading.

#### Main functions:
#####  Model visualization
After loading your models, you can obtain the parsed and visualized results of your models.
##### Drawing landscape
To draw a landscape, there are three steps:
1. **Form ODE equations** (only need for TSV models): by \'Dynamics setting\' button to generate ODE equations.
2. **Draw**: this step includes simulation and default visualization (the first two marker genes and visualization range is from 0 to 3), and corresponding to \'Draw\' button.
3. **Update**: you can adjust the marker genes and range to update the landscape by \'Update\' button; Once you make sure your visualization parameters, if you need change model related parameters, you only need to click \'Draw\' button without reupdate; Update is also worked for TME model. You can update landscape shape after load a TME model.
##### Drawing transition path
After drawing the landscape, you can draw state transition path between two attractors by specify time range, granularity, beginning and ending attractors; You can also draw path after load a TME model; Update landscape will keep paths.

For more details, please refer to the [User Manual](https://github.com/JieZheng-ShanghaiTech/TMELand/blob/main/TMELand%20Manual.pdf).


