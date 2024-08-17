import xml.etree.ElementTree as ET

def get_region_grid(name: str, path: str, locationFormat: str = "$gridLocation$") -> tuple[ET.Element, ET.Element]:
        zone_node = ET.Element(
            "VASSAL.build.module.map.boardPicker.board.mapgrid.Zone",
            attrib={
                "highlightProperty": "",
                "locationFormat": locationFormat,
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