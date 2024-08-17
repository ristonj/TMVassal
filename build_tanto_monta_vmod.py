import os
import xml.etree.ElementTree as ET
import zipfile

from builders.map_builder import MapBuilder
from builders.minor_power_builder import MinorPowerBuilder
from builders.piece_builder import PieceBuilder
from builders.power_card_builder import PowerCardBuilder
from builders.unit_builder import UnitBuilder
from models.token_common_data import TokenCommonData

def build_map(root: ET.Element, gpid: int) -> int:
    builder = MapBuilder(gpid, get_token_common_data())
    space_nodes, token_nodes = builder.build("map.xml")
    root \
        .find("./VASSAL.build.module.Map[@mapName='Map']") \
        .extend(token_nodes)
    root \
        .find(
            "./VASSAL.build.module.Map[@mapName='Map']" +
            "/VASSAL.build.module.map.BoardPicker" +
            "/VASSAL.build.module.map.boardPicker.Board[@name='Map']" +
            "/VASSAL.build.module.map.boardPicker.board.ZonedGrid") \
        .extend(space_nodes)
    return builder.gpid

def build_minor_power_diplomacy(root: ET.Element, gpid: int) -> int:
    builder = MinorPowerBuilder(gpid, get_token_common_data())
    minor_power_nodes = builder.build("minorpowers.xml")
    root \
        .find("./VASSAL.build.module.Map[@mapName='Minor Power Influence']") \
        .extend(minor_power_nodes)
    return builder.gpid

def build_pieces(root: ET.Element, gpid: int) -> int:
    builder = PieceBuilder(gpid)
    pieceNodes = builder.build("pieces.xml")
    root \
        .find("./VASSAL.build.module.PieceWindow/VASSAL.build.widget.TabWidget") \
        .extend(pieceNodes)
    return builder.gpid

def build_powercards(root: ET.Element, gpid: int) -> int:
    builder = PowerCardBuilder(gpid, get_token_common_data())
    space_nodes, token_nodes = builder.build("powercards.xml")
    root \
        .find("./VASSAL.build.module.Map[@mapName='Power Cards']") \
        .extend(token_nodes)
    root \
        .find(
            "./VASSAL.build.module.Map[@mapName='Power Cards']" +
            "/VASSAL.build.module.map.BoardPicker" +
            "/VASSAL.build.module.map.boardPicker.Board[@name='Power Cards']" +
            "/VASSAL.build.module.map.boardPicker.board.ZonedGrid") \
        .extend(space_nodes)
    return builder.gpid

def build_units(root: ET.Element, gpid: int) -> int:
    builder = UnitBuilder(gpid, get_token_common_data())
    root \
        .find("./VASSAL.build.module.Map[@mapName='Land/Naval Units']") \
        .extend(builder.buildTokens("units.xml"))
    return builder.gpid

def create_vmod(dir: str):
    imagePath = "./images"
    with zipfile.ZipFile(os.path.join(dir, "tmwip.vmod"), "w") as vmodZip:
        vmodZip.write("buildFile.xml")
        vmodZip.write("moduledata")
        for root, _, files in os.walk(imagePath):
            for file in files:
                vmodZip.write(os.path.join(root, file), 
                        os.path.relpath(
                            os.path.join(root, file), 
                            os.path.join(imagePath, '..')))

def get_token_common_data() -> TokenCommonData:
    return TokenCommonData("VASSAL.build.module.map.SetupStack", "VASSAL.build.widget.PieceSlot")

def main():
    tree = ET.parse("BaseTantoMonta.xml")
    root = tree.getroot()
    gpid = build_units(root, int(root.attrib["nextPieceSlotId"]))
    gpid = build_map(root, gpid)
    gpid = build_powercards(root, gpid)
    gpid = build_pieces(root, gpid)
    gpid = build_minor_power_diplomacy(root, gpid)
    root.attrib["nextPieceSlotId"] = str(gpid)
    ET.indent(tree, space="\t")
    tree.write("buildFile.xml", encoding="utf-8", xml_declaration=True)
    create_vmod("/mnt/c/Users/risto/OneDrive/Documents/Vassal")

if __name__ == "__main__":
    main()
