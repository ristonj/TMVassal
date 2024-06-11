import xml.etree.ElementTree as ET

from models.tokenCommonData import TokenCommonData

class MapBuilder:
    def __init__(self, gpid: int, tokenCommonData: TokenCommonData):
        self.gpid = gpid
        self.tokenCommonData = tokenCommonData

    def build_map(self, map_file: str) -> tuple[list[ET.Element], list[ET.Element]]:
        mapTree = ET.parse(map_file)
        node_list, token_list = self._get_spaces(
            mapTree.findall("./spaces/region"),
            mapTree.find("./spaceTypes")
        )
        node_list.append(self._get_vp_track(mapTree.find("./vpTrack")))
        return node_list, token_list
    
    def _get_spaces(self, regions: list[ET.Element], spaceTypes: ET.Element) -> tuple[list[ET.Element], list[ET.Element]]:
        node_list = []
        token_list = []
        for region in regions:
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
                if(folder.attrib["name"] == "None"):
                    continue
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
                    if(space.attrib["type"] in ["fortress", "standard", "strategic"]):
                        self._add_at_start_stack(folder_node, space, spaceTypes.find(
                            (f"./spaceType[@name='{space.attrib['type']}']/prototypeTokenText")) \
                            .text.format(power=folder.attrib["name"], space=space.attrib["name"], gpid=str(self.gpid))
                        )
                    elif(space.attrib["type"] == "cartographyVP"):
                        self._add_at_start_stack(
                            folder_node,
                            space,
                            spaceTypes.find(
                                "./spaceType[@name='cartographyVP']/prototypeTokenText")\
                                .text.format(
                                    name=space.attrib["name"],
                                    image=TokenCommonData.get_image_name(space.attrib["name"]) + ".png",
                                    vp="1",
                                    gpid=str(self.gpid)),
                            int(space.attrib["numVP"]))
                token_list.append(folder_node)
            node_list.append(region_node)
        return node_list, token_list
    
    def _add_at_start_stack(self, folder_node: ET.Element, space: ET.Element, text: str, num_copies: int = 1) -> None:
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
        for _ in range(num_copies):
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
            space_node.text = text
            self.gpid += 1

    def _get_vp_track(self, vp_area: ET.Element) -> ET.Element:
        vp_node = ET.Element(
            "VASSAL.build.module.map.boardPicker.board.mapgrid.Zone",
                    attrib={
                        "highlightProperty": "",
                        "locationFormat": "$gridLocation$",
                        "name" : vp_area.attrib["name"],
                        "path": vp_area.attrib["path"],
                        "useHighlight": "false",
                        "useParentGrid": "false"
                    }
        )
        vp_region = ET.SubElement(
            vp_node,
            "VASSAL.build.module.map.boardPicker.board.RegionGrid",
            attrib={
                "fontsize": "9",
                "snapto": "true",
                "visible": "false"
            }
        )
        ET.SubElement(
            vp_region,
            "VASSAL.build.module.map.boardPicker.board.Region",
            attrib={
                "name": "0",
                "originx": vp_area.attrib["zeroVPx"],
                "originy": vp_area.attrib["zeroVPy"],
            }
        )
        xInc = int(vp_area.attrib["xInc"])
        yInc = int(vp_area.attrib["yInc"])
        xCur = int(vp_area.attrib["xStart"])
        yCur = int(vp_area.attrib["yStart"])
        for i in range(1,49):
            ET.SubElement(
                vp_region,
                "VASSAL.build.module.map.boardPicker.board.Region",
                attrib={
                    "name": str(i),
                    "originx": str(xCur),
                    "originy": str(yCur)
                }
            )
            if i % 3 == 0:
                xCur = int(vp_area.attrib["xStart"])
                yCur += yInc
            else:
                xCur += xInc
        return vp_node
