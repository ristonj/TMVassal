import xml.etree.ElementTree as ET

from models.token_common_data import TokenCommonData
from models.unit_token_stack import UnitTokenStack

class UnitBuilder:
    def __init__(self, gpid: int, tokenCommonData: TokenCommonData):
        self.gpid = gpid
        self.tokenCommonData = tokenCommonData

    def add_at_start_stack(self, root: ET.Element, tokenType: ET.Element, unitTokenStack: UnitTokenStack):
        tokenName = tokenType.attrib["nameTemplate"].format(strength=unitTokenStack.strength, power=unitTokenStack.powerName, name=unitTokenStack.name)
        group, self.gpid = self.tokenCommonData.add_at_start_stack(
            gpid=self.gpid,
            tokenName=tokenName,
            owningBoard=root.find("owningBoard").attrib["name"],
            text=root.find(f"./tokenTextEntries/tokenText[@name='{tokenType.attrib['tokenText']}']").text,
            num_tokens=unitTokenStack.numTokens,
            x=unitTokenStack.xCurrent,
            y=unitTokenStack.yCurrent,
            prototype="Land\\/Naval Units",
            backCommand=self._getOptionalAttribute(tokenType, "backCommand"),
            frontCommand=self._getOptionalAttribute(tokenType, "frontCommand"),
            frontImage=tokenType.attrib["frontImage"].format(
                power=unitTokenStack.powerName.replace(" ", "").lower(),
                strength=unitTokenStack.strength.lower(),
                name=unitTokenStack.name.lower()
            ),
            backImage=self._getOptionalAttribute(tokenType, "backImage").format(
                power=unitTokenStack.powerName.replace(" ", "").lower(),
                strength=unitTokenStack.strength.lower()
            ),
            layerNames=self._getOptionalAttribute(tokenType, "layers").format(
                power=unitTokenStack.powerName,
                strength=unitTokenStack.strength
            ),
            name=tokenName
        )
        return group

    def buildTokens(self, xml_file: str) -> list[ET.Element]:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        powers = root.find("./powers")
        groups = []
        for tokens in powers.findall("./power"):
            xCurrent = tokens.attrib["xStart"]
            yCurrent = tokens.attrib["yStart"]
            for token in tokens.findall("./token"):
                tokenType = root.find(f"./tokenTypes/tokenType[@name='{token.attrib['type']}']")
                if token.attrib["numTokens"] == "0":
                    xCurrent = str(int(xCurrent) + int(tokenType.attrib["xInc"]))
                    continue
                groups.append(
                    self.add_at_start_stack(
                        root=root,
                        tokenType=tokenType,
                        unitTokenStack=UnitTokenStack(
                            xCurrent=xCurrent,
                            yCurrent=yCurrent,
                            numTokens=int(token.attrib["numTokens"]),
                            strength=self._getOptionalAttribute(token, "strength"),
                            powerName=tokens.attrib["name"],
                            name=self._getOptionalAttribute(token, "name")
                        )
                    )
                )
                xCurrent = str(int(xCurrent) + int(tokenType.attrib["xInc"]))
        return groups
    
    def _getOptionalAttribute(self, element: ET.Element, key: str) -> str:
        return element.attrib[key] if key in element.attrib.keys() else ""