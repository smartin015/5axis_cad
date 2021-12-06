import cadquery as cq
import math

G_ABS = "G90"
G_ABS_RETRACT = G_ABS + " G43 G53 G0 Z0" # 0 in machine coords is full retract 
G_REL = "G91"

rot = 0

TOOL = None
def setDefaultTool(t):
    global TOOL
    TOOL = t

class Op:
    def shouldCut(self):
        return True # Sometimes we don't want to visualize the cut, for performance reasons
    def solid(self):
        raise Exception("Unimplemented")
    def gcode(self):
        raise Exception("Unimplemented")
    def __repr__(self):
        raise Exception("Unimplemented")

class Facing(Op):
    def __init__(self, start_dia, end_dia, start_d, end_d, stepdown=1):
        self.r = [start_dia/2, end_dia/2]
        self.d = [start_d, end_d]
        self.step = stepdown
        assert(start_dia > end_dia)
        assert(start_d >= end_d)
    def solid(self):
        result = cq.Workplane("XY").circle(self.r[0]).circle(self.r[1]) \
                .extrude(self.d[1]-self.d[0]).translate((0,0,self.d[0]))
        return result
    
    def gcode(self):
        global rot 
        
        # Initial positioning; hold the spindle so it's tangent to the circular stock 
        # (cut with the side of the tool, not the bottom)
        result = [
            f";{self.__repr__()}", 
            G_ABS_RETRACT,
            f"G0 A0 X{self.r[0]+TOOL.dia/2} Y{self.d[0]-TOOL.dia/2}",
            f"G0 Z{-TOOL.shank/2}", # Note no B-axis, as it may be wound
            G_REL,
        ]
        
        # At least as many revolutions as number of full stepovers of tool diameter.
        # Increase the multiplier to get a smoother finish, at the cost of time
        nrev_mult = 1.0
        if self.d[0] - self.d[1] < 0.0001: # i.e. cutting off, not travelling on face
            nrev_deg = 360 * int((self.r[0] - self.r[1]) * nrev_mult / self.step / 10)
        else:
            nrev_deg = 360 * int((self.d[0] - self.d[1]) * nrev_mult / TOOL.dia)
        assert(nrev_deg < 9999) # Max limit of PocketNC B axis (https://pocketnc.com/pages/what-size-part)
        
        out = False
        p = self.r[0]
        dd = max(0, self.d[0]-self.d[1]-TOOL.dia/2)
        while p > self.r[1]:
            r = nrev_deg if out else -nrev_deg
            rot += r
            result += [
                # Move from end to end while spinning the stock and stepping closer each time
                # TODO: switch side of cut when rotation is reversed
                f"G1 X-{self.step} Y{dd if out else -dd} B{r}",
            ]
            p -= self.step
            out = not out
            
        # Finishing pass if needed
        if self.d[0] - self.d[1] > 0.0001:
            rot += nrev_deg
            result += [
                G_ABS, f"G1 X{self.r[1]+TOOL.dia/2}",
                G_REL, f"G1 Y{dd if out else -dd} B{nrev_deg}",
            ]
        return result
    def __repr__(self):
        return f"Facing radius {self.r} along shaft {self.d} with step {self.step}"

class Cutoff(Facing):
    def __init__(self, start_dia, d):
        super().__init__(start_dia, 0, d, d)
        
    def solid(self):
        return cq.Workplane("XY").circle(self.r[0]).circle(self.r[1]) \
                .extrude(TOOL.dia/2, both=True).translate((0,0,self.d[0]-TOOL.dia/2))
    def __repr__(self):
        return f"Cutoff @{self.d}, radius {self.r}"
        
class Polygon(Op):
    def __init__(self, start_dia, end_dia, start_d, end_d, nsides=6, stepdown=1):
        self.r = [start_dia/2, end_dia/2]
        self.d = [start_d, end_d]
        self.nsides=nsides
        self.step = stepdown
        assert(start_dia > end_dia)
        assert(start_d >= end_d)
    def solid(self):
        # params are for a *circumscribed* polygon (i.e. R is measured from center to face, not center to point)
        # so convert to an *inscribed* polygon radius which is what CADquery requires
        theta = math.pi/self.nsides
        r_outer = [self.r[0]/math.cos(theta), self.r[1]/math.cos(theta)]
        return cq.Workplane("XY").polygon(self.nsides, 2*r_outer[0]).polygon(self.nsides, 2*r_outer[1]) \
                .extrude(self.d[1]-self.d[0]).translate((0,0,self.d[0]))
    def gcode(self):
        global rot 
        
        # Initial positioning; hold the spindle so it's tangent to the circular stock 
        # (cut with the side of the tool, not the bottom)
        side_deg = 360 / self.nsides
        r = - (rot % 360) + side_deg/2
        rot += r
        result = [
            f";{self.__repr__()}", 
            G_ABS_RETRACT,
            f"G0 A0 X{self.r[0]+TOOL.dia/2} Y{self.d[0]-TOOL.dia/2}",
            f"G0 Z{-TOOL.shank/2}",
            G_REL,
            f"G0 B{r}",
        ]
        
        # Roughing passes with stepdown
        out = False
        unwind = False
        p = self.r[0]
        dd = max(0, self.d[0]-self.d[1]-TOOL.dia/2)
        
        while p > self.r[1]:
            for i in range(self.nsides):
                r = -side_deg if unwind else side_deg
                rot += r
                result += [
                    # Rotate safely to new side, out by stepdown amount
                    # TODO configurable clearance
                    G_ABS, f"G0 X{p+(TOOL.dia/2)+10}", 
                    G_REL, f"G0 B{r}", 
                    "G0 X-10",
                    # Move across and in
                    f"G1 X-{self.step} Y{dd if out else -dd}",
                    f"G0 X{self.step}",
                ]
                out = not out
            unwind = not unwind
            p -= self.step
            
            
        # Finishing pass
        for i in range(self.nsides):
            r = -side_deg if unwind else side_deg
            rot += r
            result += [
                # Rotate safely to new side, out by stepdown amount
                G_ABS, f"G0 X{self.r[1] + (TOOL.dia/2) + 10}", 
                G_REL, f"G0 B{r}", 
                "G0 X-10",
                # Move across
                G_REL, f"G1 Y{dd if out else -dd}",
            ]
            out = not out
        return result
    def __repr__(self):
        return f"Polygon inscribed radius {self.r} along shaft {self.d} with step {self.step}"
        
class Bore(Op):
    def __init__(self, start_d, end_d, dia, stepdown_per_rev=1):
        self.d = [start_d, end_d]
        self.dia = dia
        self.step = stepdown_per_rev
        assert(start_d > end_d)
        assert(dia >= TOOL.dia)
    def gcode(self):
        global rot 
        
        # Initial positioning, bit parallel to stock axis
        result = [
            f";{self.__repr__()}", 
            G_ABS_RETRACT,
            f"G0 A90 X{(self.dia-TOOL.dia)/2} Y0 Z{self.d[0]}",
            G_REL,
        ]
        
        nrev_mult = 1.0
        nrev_deg = 360 * int((self.d[0] - self.d[1]) * nrev_mult / self.step)
        assert(nrev_deg < 9999) # Max limit of PocketNC B axis (https://pocketnc.com/pages/what-size-part)
        
        # Two operations to allow for fully unwinding over the course of the cut
        result += [
            f"G1 Z{(self.d[1]-self.d[0])/2} B{nrev_deg/2}",
            f"G1 Z{(self.d[1]-self.d[0])/2} B{-nrev_deg/2}",
        ]
        return result
        
        
    def solid(self):
        return cq.Workplane("XY").circle(self.dia/2) \
                .extrude(self.d[1]-self.d[0]).translate((0,0,self.d[0]))
    def __repr__(self):
        return f"Bore @{self.d}, dia {self.dia} step {self.step}"

class Threading(Op):
    def __init__(self, dia, start_d, end_d, pitch):
        self.d = [start_d, end_d]
        self.dia = dia
        self.pitch = pitch
        assert(start_d > end_d)
        assert(dia >= TOOL.dia)
    def gcode(self):
        global rot 
        
        # Initial positioning, bit parallel to stock axis
        result = [
            f";{self.__repr__()}", 
            G_ABS_RETRACT,
            f"G0 A0 X{(self.dia-TOOL.dia)/2} Y0 Z{self.d[0]}",
            G_REL,
        ]
        
        nrev_deg = 360 * (self.d[0] - self.d[1]) / self.pitch
        assert(nrev_deg < 9999) # Max limit of PocketNC B axis (https://pocketnc.com/pages/what-size-part)
        
        # Two operations to allow for fully unwinding over the course of the cut
        result.append(f"G1 Z{(self.d[1]-self.d[0])} B{nrev_deg}")
        
        # Unwind
        result += [
            G_ABS_RETRACT,
            f"G1  B{-nrev_deg}"
        ]
        return result
    def shouldCut(self):
        return False # Thread cutting stalls the kernel :'(
    def solid(self):
        thread_profile = cq.Workplane("YZ",origin=(0,self.dia/2,0)).circle(min(self.pitch/4, 1.0))
        # Pitch, height, radius, angle
        path = cq.Workplane("XY", obj=cq.Wire.makeHelix(self.pitch, self.d[0] - self.d[1], self.dia/2))
        return thread_profile.sweep(path).translate((0,0,self.d[1]))
        # return cq.Workplane("XY").box(5,5,5)
        
    def __repr__(self):
        return f"Thread @{self.d}, dia {self.dia} pitch {self.pitch}"

