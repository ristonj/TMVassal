import xml.etree.ElementTree as ET

from models.tokenCommonData import TokenCommonData
from models.unitTokenStack import UnitTokenStack

class UnitBuilder:
    def __init__(self, gpid: int):
        self.gpid = gpid

    def addAtStartStack(self, root: ET.Element, tokenCommonData: TokenCommonData, tokenType: ET.Element, unitTokenStack: UnitTokenStack):
        tokenName = tokenType.attrib["nameTemplate"].format(strength=unitTokenStack.strength, power=unitTokenStack.powerName, name=unitTokenStack.name)
        group = ET.Element(
            tokenCommonData.parent,
            attrib={
                "name": tokenName,
                "owningBoard": root.find("owningBoard").attrib["name"],
                "useGridLocation": "false",
                "x": unitTokenStack.xCurrent,
                "y": unitTokenStack.yCurrent
            }
        )
        for _ in range(int(unitTokenStack.numTokens)):
            ET.SubElement(
                group,
                tokenCommonData.child,
                attrib={
                    "entryName": tokenName,
                    "gpid": str(self.gpid),
                    "height": root\
                        .find(f"./tokenDimensions/dimension[@type='{tokenType.attrib['dimension']}']")\
                        .attrib["height"],
                    "width": root\
                        .find(f"./tokenDimensions/dimension[@type='{tokenType.attrib['dimension']}']")\
                        .attrib["width"]
                }
            ).text=\
                root.find(f"./tokenTextEntries/tokenText[@name='{tokenType.attrib['tokenText']}']")\
                    .text.format(
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
            self.gpid += 1
        return group

    def buildTokens(self, xml_file: str, gpid: int) -> list[ET.Element]:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        powers = root.find("./powers")
        groups = []
        tokenCommonData = self.getTokenCommonData(root)
        for tokens in powers.findall("./power"):
            xCurrent = tokens.attrib["xStart"]
            yCurrent = tokens.attrib["yStart"]
            for token in tokens.findall("./token"):
                tokenType = root.find(f"./tokenTypes/tokenType[@name='{token.attrib['type']}']")
                if token.attrib["numTokens"] == "0":
                    xCurrent = str(int(xCurrent) + int(tokenType.attrib["xInc"]))
                    continue
                groups.append(
                    self.addAtStartStack(
                        root=root,
                        tokenCommonData=tokenCommonData,
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

    def getTokenCommonData(self, root: ET.Element):
        return TokenCommonData(
            parent=root.find("./tokenGroupParent").attrib["name"],
            child=root.find("./tokenGroupChild").attrib["name"]
        )
    
    def _getOptionalAttribute(self, element: ET.Element, key: str) -> str:
        return element.attrib[key] if key in element.attrib.keys() else ""