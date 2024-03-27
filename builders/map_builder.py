import xml.etree.ElementTree as ET

from models.tokenCommonData import TokenCommonData

class MapBuilder:
    def __init__(self, gpid: int, token_common_data: TokenCommonData, root: ET.Element):
        self.gpid = gpid
        self.token_common_data = token_common_data
        self.root = root

    def build_map(self, map_file: str) -> list[ET.Element]:
        mapBoardNode = self.root.find("./VASSAL.build.module.map.BoardPicker/VASSAL.build.module.map.boardPicker.Board[@name='Map']/VASSAL.build.module.map.boardPicker.board.ZonedGrid")
        mapTree = ET.parse(map_file)
        node_list = []
        for region in mapTree.findall("./spaces/region"):
            region_node = ET.SubElement(
                mapBoardNode,
                "VASSAL.build.module.map.boardPicker.board.mapgrid.Zone",
                attrib={
                    "highlightProperty": "",
                    "locationFormat": "$gridLocation$",
                    "name" : region.attrib["name"],
                    "path": region.attrib["path"],
                    "useHighlight": "false",
                    "useParentGrid": "false"
                })
            region_grid_node = ET.SubElement(
                region_node,
                "VASSAL.build.module.map.boardPicker.board.RegionGrid",
                attrib={
                    "fontsize": "9",
                    "snapto": "true",
                    "visible": "false"
                })
            for space in region.findall("./space"):
                ET.SubElement(
                    region_grid_node,
                    "VASSAL.build.module.map.boardPicker.board.Region",
                    attrib={
                        "name": space.attrib["name"],
                        "originx": space.attrib["x"],
                        "originy": space.attrib["y"]
                    }
                )
            node_list.append(region_node)
        return node_list
