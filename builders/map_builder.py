import xml.etree.ElementTree as ET

from models.tokenCommonData import TokenCommonData

class MapBuilder:
    def __init__(self, gpid: int, tokenCommonData: TokenCommonData):
        self.gpid = gpid
        self.tokenCommonData = tokenCommonData

    def build_map(self, map_file: str) -> tuple[list[ET.Element], list[ET.Element]]:
        mapTree = ET.parse(map_file)
        node_list, token_list = self._get_spaces(
            mapTree.findall("./spaces/zone"),
            mapTree.find("./spaceTypes")
        )
        node_list.append(self._get_vp_track(mapTree.find("./vpTrack")))
        france_influence_list, france_influence_token_list = self._get_france_influence(
            mapTree.find("./franceInfluenceTracks"),
            mapTree.find("./spaceTypes/spaceType[@name='franceInfluenceMarker']/prototypeTokenText").text,
            mapTree.find("./spaceTypes/spaceType[@name='franceHouseVP']/prototypeTokenText").text)
        node_list.extend(france_influence_list)
        token_list.extend(france_influence_token_list)
        return node_list, token_list
    
    def _get_spaces(self, zones: list[ET.Element], spaceTypes: ET.Element) -> tuple[list[ET.Element], list[ET.Element]]:
        node_list = []
        token_list = []
        for zone in zones:
            zone_node, region_grid_node = self._get_region_grid(zone.attrib["name"], zone.attrib["path"])
            for folder in zone.findall("./folder"):
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
                        self._add_at_start_stack(
                            folder_node,
                            space.attrib["name"],
                            space.attrib["x"],
                            space.attrib["y"],
                            spaceTypes.find(
                                (f"./spaceType[@name='{space.attrib['type']}']/prototypeTokenText")) \
                                .text \
                                .format(power=folder.attrib["name"], space=space.attrib["name"], gpid=str(self.gpid))
                        )
                    elif(space.attrib["type"] == "onmapVP"):
                        self._add_at_start_stack(
                            folder_node,
                            space.attrib["name"],
                            space.attrib["x"],
                            space.attrib["y"],
                            spaceTypes.find(
                                "./spaceType[@name='onmapVP']/prototypeTokenText")\
                                .text.format(
                                    name=space.attrib["name"],
                                    image=TokenCommonData.get_image_name(space.attrib["name"]) + ".png",
                                    vp=space.attrib["vp"],
                                    gpid=str(self.gpid)),
                            int(space.attrib["num"]))
                token_list.append(folder_node)
            node_list.append(zone_node)
        return node_list, token_list
    
    def _add_at_start_stack(self, folder_node: ET.Element, name: str, x: str, y: str, text: str, num_copies: int = 1) -> None:
        tokenStack = ET.SubElement(
            folder_node,
            self.tokenCommonData.parent,
            attrib={
                "name": name,
                "owningBoard": "Map",
                "useGridLocation": "false",
                "x": x,
                "y": y
            }
        )
        for _ in range(num_copies):
            space_node = ET.SubElement(
                tokenStack,
                self.tokenCommonData.child,
                attrib={
                    "entryName": name,
                    "gpid": str(self.gpid),
                    "height": "64",
                    "width": "75"
                }
            )
            space_node.text = text
            self.gpid += 1

    def _get_vp_track(self, vp_area: ET.Element) -> ET.Element:
        vp_node, vp_region = self._get_region_grid(vp_area.attrib["name"], vp_area.attrib["path"])
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
    
    def _get_france_influence(
            self,
            france_influence_tracks: ET.Element,
            marker_text: str,
            vp_text: str) -> tuple[list[ET.Element], list[ET.Element]]:
        node_list = []
        token_list = []
        folder_node = ET.Element(
                    "VASSAL.build.module.folder.MapSubFolder",
                    attrib={
                        "desc": "",
                        "name": "France Influence Tracks"
                    }
                )
        for track in france_influence_tracks.findall("./track"):
            zone_node, region_grid_node = self._get_region_grid(track.attrib["name"], track.attrib["path"])
            if("isNavarre" in track.attrib):
                ET.SubElement(
                    region_grid_node,
                    "VASSAL.build.module.map.boardPicker.board.Region",
                    attrib={
                        "name": "Start",
                        "originx": track.attrib["xStart"],
                        "originy": track.attrib["yStart"]
                    }
                )
                ET.SubElement(
                    region_grid_node,
                    "VASSAL.build.module.map.boardPicker.board.Region",
                    attrib={
                        "name": "3 (Military)",
                        "originx": str(int(track.attrib["xStart"]) + int(track.attrib["xInc"])),
                        "originy": track.attrib["yStart"]
                    }
                )
                ET.SubElement(
                    region_grid_node,
                    "VASSAL.build.module.map.boardPicker.board.Region",
                    attrib={
                        "name": "5 (Political)",
                        "originx": str(int(track.attrib["xStart"]) + 2 * int(track.attrib["xInc"])),
                        "originy": track.attrib["yStart"]
                    }
                )
                self._add_at_start_stack(
                    folder_node,
                    track.attrib["name"],
                    track.attrib["xStart"],
                    track.attrib["yStart"],
                    marker_text.format(
                        name=track.attrib["name"],
                        image=TokenCommonData.get_image_name(track.attrib["name"], False) + "influence.png",
                        gpid=str(self.gpid)
                    )
                )
            else:
                for i in range(-1, int(track.attrib["numSpaces"]) - 1):
                    if i == -1:
                        name = "Start"
                        self._add_at_start_stack(
                            folder_node,
                            track.attrib["name"],
                            track.attrib["xStart"],
                            track.attrib["yStart"],
                            marker_text.format(
                                name=track.attrib["name"],
                                image=TokenCommonData.get_image_name(track.attrib["name"]) + "influence.png",
                                gpid=str(self.gpid)
                            )
                        )
                    else:
                        name = str(i)
                    ET.SubElement(
                        region_grid_node,
                        "VASSAL.build.module.map.boardPicker.board.Region",
                        attrib={
                            "name": name,
                            "originx": str(int(track.attrib["xStart"]) + (i + 1) * int(track.attrib["xInc"])),
                            "originy": track.attrib["yStart"]
                        }
                    )
                self._add_at_start_stack(
                    folder_node,
                    track.attrib["name"],
                    str(int(track.attrib["xStart"]) + (int(track.attrib["numSpaces"]) - 1) * int(track.attrib["xInc"])),
                    track.attrib["yStart"],
                    vp_text.format(
                        name=track.attrib["name"],
                        image=TokenCommonData.get_image_name(track.attrib["name"]) + "housevp.png",
                        gpid=str(self.gpid)
                    )
                )
            node_list.append(zone_node)
        token_list.append(folder_node)
        return node_list, token_list

    def _get_region_grid(self, name: str, path: str) -> tuple[ET.Element, ET.Element]:
        zone_node = ET.Element(
            "VASSAL.build.module.map.boardPicker.board.mapgrid.Zone",
                    attrib={
                        "highlightProperty": "",
                        "locationFormat": "$gridLocation$",
                        "name" : name,
                        "path": path,
                        "useHighlight": "false",
                        "useParentGrid": "false"
                    }
        )
        region_grid_node = ET.SubElement(
            zone_node,
            "VASSAL.build.module.map.boardPicker.board.RegionGrid",
            attrib={
                "fontsize": "9",
                "snapto": "true",
                "visible": "false"
            }
        )
        return zone_node, region_grid_node
