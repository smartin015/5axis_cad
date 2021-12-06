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
