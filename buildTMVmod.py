import os
import xml.etree.ElementTree as ET
import zipfile

from builders.map_builder import MapBuilder
from builders.piece_builder import PieceBuilder
from builders.power_card_builder import PowerCardBuilder
from builders.unit_builder import UnitBuilder
from models.tokenCommonData import TokenCommonData

def build_map(root: ET.Element, gpid: int) -> int:
    builder = MapBuilder(gpid, getTokenCommonData())
    spaceNodes, tokenNodes = builder.build_map("map.xml")
    root \
        .find("./VASSAL.build.module.Map[@mapName='Map']") \
        .extend(tokenNodes)
    root \
        .find(
            "./VASSAL.build.module.Map[@mapName='Map']" +
            "/VASSAL.build.module.map.BoardPicker" +
            "/VASSAL.build.module.map.boardPicker.Board[@name='Map']" +
            "/VASSAL.build.module.map.boardPicker.board.ZonedGrid") \
        .extend(spaceNodes)
    return builder.gpid

def build_pieces(root: ET.Element, gpid: int) -> int:
    builder = PieceBuilder(gpid)
    pieceNodes = builder.build_pieces("pieces.xml")
    root \
        .find("./VASSAL.build.module.PieceWindow/VASSAL.build.widget.TabWidget") \
        .extend(pieceNodes)
    return builder.gpid

def build_powercards(root: ET.Element, gpid: int) -> int:
    builder = PowerCardBuilder(gpid, getTokenCommonData())
    root \
        .find("./VASSAL.build.module.Map[@mapName='Power Cards']") \
        .extend(builder.buildPowerCards("powercards.xml"))
    return builder.gpid

def build_units(root: ET.Element, gpid: int) -> int:
    builder = UnitBuilder(gpid, getTokenCommonData())
    root \
        .find("./VASSAL.build.module.Map[@mapName='Land/Naval Units']") \
        .extend(builder.buildTokens("units.xml"))
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
    gpid = build_units(root, int(root.attrib["nextPieceSlotId"]))
    gpid = build_map(root, gpid)
    gpid = build_powercards(root, gpid)
    gpid = build_pieces(root, gpid)
    root.attrib["nextPieceSlotId"] = str(gpid)
    ET.indent(tree, space="\t")
    tree.write("buildFile.xml", encoding="utf-8", xml_declaration=True)
    createVmod("/mnt/c/Users/risto/OneDrive/Documents/Vassal")

if __name__ == "__main__":
    main()
