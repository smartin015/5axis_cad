
class Tool:
    def __init__(self, dia, shank, rpm):
        self.dia = dia
        self.shank = shank
        self.rpm = rpm

ENDMILL_0125in = Tool(3.1750, 10, 25000)
ENDMILL_4mm = Tool(4, 10, 25000)
