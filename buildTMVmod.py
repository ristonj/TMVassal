import os
import xml.etree.ElementTree as ET
import zipfile

from builders.unit_builder import UnitBuilder
from builders.map_builder import MapBuilder

def build_units(root: ET.Element, gpid: int) -> int:
    builder = UnitBuilder(gpid)
    infantryNodes = builder.buildTokens("units.xml", gpid)
    infantryRoot = root.find("./VASSAL.build.module.Map[@mapName='Land/Naval Units']")
    for node in infantryNodes:
        infantryRoot.append(node)
    return builder.gpid

def build_map(root: ET.Element, gpid: int) -> int:
    builder = MapBuilder(gpid, "blah", root)
    mapRoot = root.find("./VASSAL.build.module.Map[@mapName='Main Map']/VASSAL.build.module.map.BoardPicker/VASSAL.build.module.map.boardPicker.Board[@name='Map']/VASSAL.build.module.map.boardPicker.board.ZonedGrid")
    mapNodes = builder.build_map("map.xml")
    for node in mapNodes:
        mapRoot.append(node)
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

def main():
    tree = ET.parse("BaseTantoMonta.xml")
    root = tree.getroot()
    gpid = build_units(root, int(root.attrib["nextPieceSlotId"]))
    root.attrib["nextPieceSlotId"] = str(gpid)
    gpid = build_map(root, gpid)
    ET.indent(tree, space="\t", level=0)
    tree.write("buildFile.xml", encoding="utf-8")
    # createVmod("/mnt/c/Users/risto/OneDrive/Documents/Vassal")

if __name__ == "__main__":
    main()