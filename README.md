# 5-axis CNC gcode generator for PocketNC

This is a set of CADQuery based operations for turning operations on the PocketNC 5-axis CNC machine.

See `examples/` for example notebooks.

# DANGER DANGER DANGER

This library contains very unproven methods for controlling machinery that use sharp spinning blades to cut metal and other materials.

If you decide to use this library, you use it at your own risk.

## Safety

* Never run generated GCODE on a physical machine without appropriate enclosure/personal protective equipment
* Always triple-check gcode behavior using a simulator (for PocketNC, this is https://sim.pocketnc.com/)
* Run the cut files without any stock loaded first, to ensure no unexpected behavior / crashing occurs.

## Installation

This toolset uses [jupyter-cadquery](https://github.com/bernhard-42/jupyter-cadquery) as an environment for
visualizing and tweaking cut operations before export. Installation has been tested only on linux and may require tweaks for other OSes

Installation instructions are similar to the jupyter-cadquery instructions, but including this repo as a package:

```shell
conda create -n jcq22 -c conda-forge -c cadquery python=3.8 cadquery
conda activate jcq22
pip install jupyter-cadquery==2.2.1 matplotlib

# To install mainline version
pip install cad_5axis

# For development
conda install conda-build 
conda develop /path/to/this/repository
```

## Usage

Browse in jupyter lab to the `examples/` folders and click around for various usage examples.

Every notebook should start by setting up the environment and importing the modules like so:

```python
from cad_5axis.jcqsetup import op, tool, post
op.setDefaultTool(tool.ENDMILL_0125in)
```

The meat of the notebook defines constants, creates a list of sequential cutting operations, and then calls `post.render(...)` to 
get gcode, a solid representing the result of the operations applied to cylindrical stock, and a jupyter-cadquery `PartGroup` which
can be shown in the lab sidecar by invoking it:

```python
# Example threaded shaft for dremel chuck
STOCK_LEN = 30
STOCK_DIA = 10
THREAD_DIA = .275 * 25.4
THREAD_PITCH = 40 / 25.4
BORE_DIA = 4

P_TOP = STOCK_LEN+1
P_MID = STOCK_LEN/2
P_BOT = 0

ops = [
    op.Facing(STOCK_DIA, (THREAD_DIA+0.003), P_TOP, P_MID),
    op.Threading(THREAD_DIA, P_TOP, P_MID + 5, THREAD_PITCH),
    op.Bore(P_TOP, P_MID - 5, BORE_DIA),
]

gcode, solid, pg = post.render(STOCK_DIA, STOCK_LEN, ops)
pg
```

Finally, call `post.export(...)` to write a `*.nc` containing gcode and `*.stl` file for visualization. The last argument is a base filename
for the written files:

```python
post.export(gcode, solid, "dremel_chuck_adapter")
```

The outputs of `export` can be imported into the [PocketNC simulator](http://sim.pocketnc.com) and run to verify expected behavior.
