import os
import xml.dom
import xml.etree.ElementTree as ET
import zipfile

from builders.map_builder import MapBuilder
from builders.power_card_builder import PowerCardBuilder
from builders.unit_builder import UnitBuilder
from models.tokenCommonData import TokenCommonData

def build_map(root: ET.Element, gpid: int, tokenCommonData: TokenCommonData) -> int:
    builder = MapBuilder(gpid, tokenCommonData)
    mapRoot = root.find("./VASSAL.build.module.Map[@mapName='Main Map']")
    gridRoot = root.find("./VASSAL.build.module.Map[@mapName='Main Map']/VASSAL.build.module.map.BoardPicker/VASSAL.build.module.map.boardPicker.Board[@name='Map']/VASSAL.build.module.map.boardPicker.board.ZonedGrid")
    mapNodes, tokenNodes = builder.build_map("map.xml")
    for node in mapNodes:
        gridRoot.append(node)
    for node in tokenNodes:
        mapRoot.append(node)
    return builder.gpid

def build_powercards(root: ET.Element, gpid: int, tokenCommonData: TokenCommonData) -> int:
    builder = PowerCardBuilder(gpid, tokenCommonData)
    powerCardRoot = root.find("./VASSAL.build.module.Map[@mapName='Power Cards']")
    powerCardNodes = builder.buildPowerCards("powercards.xml")
    for node in powerCardNodes:
        powerCardRoot.append(node)
    return builder.gpid

def build_units(root: ET.Element, gpid: int, tokenCommonData: TokenCommonData) -> int:
    builder = UnitBuilder(gpid, tokenCommonData)
    infantryNodes = builder.buildTokens("units.xml")
    infantryRoot = root.find("./VASSAL.build.module.Map[@mapName='Land/Naval Units']")
    for node in infantryNodes:
        infantryRoot.append(node)
    return builder.gpid

def createVmod(dir: str):
    imagePath = "./images"
    with zipfile.ZipFile(os.path.join(dir, "tmwip.vmod"), "w") as vmodZip:
        vmodZip.write("buildFile.xml")
        vmodZip.write("moduledata")
        for root, _, files in os.walk(imagePath):
            for file in files:
                vmodZip.write(os.path.join(root, file), 
                        os.path.relpath(os.path.join(root, file), 
                                        os.path.join(imagePath, '..')))

def getTokenCommonData() -> TokenCommonData:
    return TokenCommonData("VASSAL.build.module.map.SetupStack", "VASSAL.build.widget.PieceSlot")

def main():
    tree = ET.parse("BaseTantoMonta.xml")
    root = tree.getroot()
    tokenCommonData = getTokenCommonData()
    gpid = build_units(root, int(root.attrib["nextPieceSlotId"]), tokenCommonData)
    gpid = build_map(root, gpid, tokenCommonData)
    gpid = build_powercards(root, gpid, tokenCommonData)
    root.attrib["nextPieceSlotId"] = str(gpid)
    ET.indent(tree, space="\t")
    tree.write("buildFile.xml", encoding="utf-8", xml_declaration=True)
    createVmod("/mnt/c/Users/risto/OneDrive/Documents/Vassal")

if __name__ == "__main__":
    main()
