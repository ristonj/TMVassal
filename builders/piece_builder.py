import xml.etree.ElementTree as ET

class PieceBuilder:
    def __init__(self, gpid: int):
        self.gpid = gpid

    def build_pieces(self, piece_file: str) -> list[ET.Element]:
        pieceTree = ET.parse(piece_file)
        piece_list = self._get_nonvp_pieces(
            pieceTree.findall("./nonVP/panel"),
            pieceTree.find("./tokenTexts/tokenText[@name='singleSidedPiece']").text
        )
        piece_list.append(self._get_vp_pieces(
            pieceTree.find("./VP"),
            pieceTree.find("./tokenTexts")
        ))
        return piece_list
    
    def _get_nonvp_pieces(self, pieceTree: list[ET.Element], tokenText: str) -> list[ET.Element]:
        piece_list = []
        for panel in pieceTree:
            panel_element = ET.Element(
                "VASSAL.build.widget.ListWidget",
                attrib={
                    "divider": panel.attrib["divider"],
                    "entryName": panel.attrib["name"],
                    "height": panel.attrib["height"],
                    "scale": "1.0",
                    "width": panel.attrib["width"]
                })
            for piece in panel.findall("./singleSidedPiece"):
                self._get_subelement(
                    panel_element,
                    piece.attrib["name"]
                ).text = tokenText.format(
                    image=self._get_image_name(piece.attrib["name"]) + ".png",
                    name=piece.attrib["name"],
                    gpid=str(self.gpid)
                )
                self.gpid += 1
            piece_list.append(panel_element)
        return piece_list
    
    def _get_image_name(self, name: str) -> str:
        return name \
            .replace(" ", "") \
            .replace("(", "") \
            .replace(")", "") \
            .replace("+", "plus") \
            .replace("-", "minus") \
            .lower()

    def _get_vp_pieces(self, vp_node: ET.Element, tokenTexts: ET.Element) -> ET.Element:
        panel = ET.Element(
            "VASSAL.build.widget.ListWidget",
            attrib={
                "divider": vp_node.attrib["divider"],
                "entryName": "VP",
                "height": vp_node.attrib["height"],
                "scale": "1.0",
                "width": vp_node.attrib["width"]
            })
        for vp_piece in vp_node.findall("./singleVP"):
            self._get_subelement(
                panel,
                vp_piece.attrib["name"]
            ).text = tokenTexts.find("./tokenText[@name='singleVP']").text.format(
                name=vp_piece.attrib["name"],
                image=self._get_image_name(vp_piece.attrib["name"]) + "vp.png",
                vp=vp_piece.attrib["VP"],
                gpid=str(self.gpid)
            )
            self.gpid += 1
        return panel

    def _get_subelement(self, panel_element: ET.Element, name: str) -> ET.Element:
        return ET.SubElement(
            panel_element,
            "VASSAL.build.widget.PieceSlot",
            attrib={
                "entryName": name,
                "gpid": str(self.gpid),
                "height": "64",
                "width": "75"
            },
        )
