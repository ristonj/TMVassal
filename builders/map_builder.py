import xml.etree.ElementTree as ET

from models.tokenCommonData import TokenCommonData

class MapBuilder:
    def __init__(self, gpid: int, tokenCommonData: TokenCommonData):
        self.gpid = gpid
        self.tokenCommonData = tokenCommonData

    def build_map(self, map_file: str) -> tuple[list[ET.Element], list[ET.Element]]:
        mapTree = ET.parse(map_file)
        node_list = []
        token_list = []
        for region in mapTree.findall("./spaces/region"):
            region_node = ET.Element(
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
            for folder in region.findall("./folder"):
                folder_node = ET.Element(
                    "VASSAL.build.module.folder.MapSubFolder",
                    attrib={
                        "desc": "",
                        "name": folder.attrib["name"]
                    }
                )
                for space in folder.findall("./space"):
                    ET.SubElement(
                        region_grid_node,
                        "VASSAL.build.module.map.boardPicker.board.Region",
                        attrib={
                            "name": space.attrib["name"],
                            "originx": space.attrib["x"],
                            "originy": space.attrib["y"]
                        }
                    )
                    if(space.attrib["type"] in ["fortress", "standard"]):
                        tokenStack = ET.SubElement(
                            folder_node,
                            self.tokenCommonData.parent,
                            attrib={
                                "name": space.attrib["name"],
                                "owningBoard": "Map",
                                "useGridLocation": "false",
                                "x": space.attrib["x"],
                                "y": space.attrib["y"]
                            }
                        )
                        space_node = ET.SubElement(
                            tokenStack,
                            self.tokenCommonData.child,
                            attrib={
                                "entryName": space.attrib["name"],
                                "gpid": str(self.gpid),
                                "height": "64",
                                "width": "75"
                            }
                        )
                        space_node.text = mapTree.find(f"./spaceTypes/spaceType[@name='{space.attrib['type']}']/prototypeTokenText") \
                            .text.format(power=folder.attrib["name"])
                        self.gpid += 1
                token_list.append(folder_node)
            node_list.append(region_node)
        return node_list, token_list
