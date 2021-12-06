from jupyter_cadquery import set_defaults, set_sidecar
from jupyter_cadquery.cadquery import (PartGroup, Part, show) # These are used to display your models in Jupyter Lab
import math

set_defaults(theme="dark") # Comment this out if you use a light theme
set_sidecar("CadQuery", init=True)
import cadquery as cq

from cad_5axis import ops, tools, post
op = ops
tool = tools
post = post

print(f"Imported cadquery version {cq.__version__}")