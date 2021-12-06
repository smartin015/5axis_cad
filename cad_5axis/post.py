import cadquery as cq 
from jupyter_cadquery.cadquery import (PartGroup, Part)

def export(gcode, solid, prefix="out"):
    path = prefix + ".nc"
    with open(path, "w") as f:
        f.write(gcode)
    print("Wrote ", path)

    path = prefix + ".stl"
    cq.exporters.export(solid.rotate((0,0,0),(1,0,0),-90), path)
    print("Wrote ", path)

def gcode(ops):
    gcode = """; CADQuery 5-axis lathe notebook - Scott Martin 2021Q4
    ; Begin startup
    G21
    G90 G94 G40 G17
    M5
    M0
    T4 M6
    G21
    G43
    G90 G43 G53 G0 Z0
    M0 ; Insert stock piece, loosely
    G90 G0 A90 X0 Y0
    G0 Z30
    M0 ; Slide stock to spindle and tighten
    ; End startup
    S47000 M3
    F200
    """
    gcode += "\n".join([l for op in ops for l in op.gcode()])
    gcode += """
    ; Begin closeout
    G90 G53 Z0
    G49

    M5
    M30
    ; End closeout
    """
    return gcode

def asPart(op):
    return Part(op.solid(), op.__class__.__name__, show_faces=False)

def render(stock_dia, stock_len, ops):
    stock = cq.Workplane("XY").circle(stock_dia/2).extrude(stock_len)
    solid = stock
    for op in ops:
        if op.shouldCut():
            solid = solid.cut(op.solid())
    
    return (
        gcode(ops),
        solid, 
        PartGroup([asPart(op) for op in ops] + [Part(solid, "result"), Part(stock, "stock", show_faces=False)])
    )
    
