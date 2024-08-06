class UnitTokenStack:
    def __init__(
            self,
            xCurrent: str,
            yCurrent: str,
            numTokens: int,
            strength: str, 
            powerName: str,
            name: str):
        self.xCurrent = xCurrent
        self.yCurrent = yCurrent
        self.numTokens = numTokens
        self.strength = strength
        self.powerName = powerName
        self.name = name