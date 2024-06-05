import xml.etree.ElementTree as ET

class PieceBuilder:
    def __init__(self, gpid: int):
        self.gpid = gpid

    def build_pieces(self, piece_file: str) -> list[ET.Element]:
        pieceTree = ET.parse(piece_file)
        return self._get_nonvp_pieces(
            pieceTree.findall("./nonVP/panel"),
            pieceTree.find("./tokenTexts/tokenText[@name='singleSidedPiece']").text
        )
    
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
                ET.SubElement(
                    panel_element,
                    "VASSAL.build.widget.PieceSlot",
                    attrib={
                        "entryName": piece.attrib["name"],
                        "gpid": str(self.gpid),
                        "height": "64",
                        "width": "75"
                    },
                ).text = tokenText.format(
                    image=piece.attrib["name"] \
                        .replace(" ", "") \
                        .replace("(", "") \
                        .replace(")", "") \
                        .replace("+", "plus") \
                        .replace("-", "minus") \
                        .lower() + ".png",
                    name=piece.attrib["name"],
                    gpid=str(self.gpid)
                )
                self.gpid += 1
            piece_list.append(panel_element)
        return piece_list
