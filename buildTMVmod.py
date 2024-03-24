import os
import xml.etree.ElementTree as ET
import zipfile

from models.tokenCommonData import TokenCommonData
from models.unitTokenStack import UnitTokenStack

class BuildTMVmod:
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
        powers=root.find("./powers")
        return TokenCommonData(
            parent=root.find("./tokenGroupParent").attrib["name"],
            child=root.find("./tokenGroupChild").attrib["name"]
        )
    
    def _getOptionalAttribute(self, element: ET.Element, key: str) -> str:
        return element.attrib[key] if key in element.attrib.keys() else ""

def createVmod(dir: str):
    imagePath = "./images"
    with zipfile.ZipFile(os.path.join(dir, "tmwip.vmod"), "w") as vmodZip:
        vmodZip.write("buildFile.xml")
        vmodZip.write("moduledata")
        for root, dirs, files in os.walk(imagePath):
            for file in files:
                vmodZip.write(os.path.join(root, file), 
                        os.path.relpath(os.path.join(root, file), 
                                        os.path.join(imagePath, '..')))

def main():
    tree = ET.parse("BaseTantoMonta.xml")
    root = tree.getroot()
    initGPID = int(root.attrib["nextPieceSlotId"])
    builder = BuildTMVmod(initGPID)
    infantryNodes = builder.buildTokens("units.xml", initGPID)
    root.attrib["nextPieceSlotId"] = str(builder.gpid)
    infantryRoot = root.find("./VASSAL.build.module.Map[@mapName='Land/Naval Units']")
    for node in infantryNodes:
        infantryRoot.append(node)
    
    ET.indent(tree, space="\t", level=0)
    tree.write("buildFile.xml", encoding="utf-8")
    createVmod("/mnt/c/Users/risto/OneDrive/Documents/Vassal")

if __name__ == "__main__":
    main()