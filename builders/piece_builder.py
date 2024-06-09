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
                    piece.attrib["name"],
                    tokenText.format(
                        image=self._get_image_name(piece.attrib["name"]) + ".png",
                        name=piece.attrib["name"],
                        gpid=str(self.gpid)
                    )
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
        for vp_piece in vp_node:
            text = ""
            match vp_piece.tag:
                case "singleVP":
                    text = tokenTexts.find("./tokenText[@name='singleVP']").text.format(
                        name=vp_piece.attrib["name"],
                        image=self._get_image_name(vp_piece.attrib["name"]) + "vp.png",
                        vp=vp_piece.attrib["VP"],
                        gpid=str(self.gpid)
                    )
                case "multiVP":
                    max_vp = int(vp_piece.attrib["maxVP"])
                    step = 1
                    if "step" in vp_piece.attrib:
                        step = int(vp_piece.attrib["step"])
                    min_vp = self._get_min_value(step, max_vp)
                    text = tokenTexts.find("./tokenText[@name='multiVP']").text.format(
                        name=vp_piece.attrib["name"],
                        step=str(step),
                        minVP=str(min_vp),
                        maxVP=str(max_vp),
                        images=",".join([
                            self._get_image_name(vp_piece.attrib["name"]) + str(i) + "vp.png" \
                                  for i in range(
                                      min_vp,
                                      max_vp + 1,
                                      step)
                        ]),
                        vpLevels=",".join([str(i) + " VP" \
                            for i in range(
                                min_vp,
                                max_vp + 1,
                                step)
                        ]),
                        gpid=str(self.gpid)
                    )
                case "anfa":
                    text=tokenTexts.find("./tokenText[@name='anfa']").text
            if "name" in vp_piece.attrib:
                self._get_subelement(panel, vp_piece.attrib["name"], text)
            else:
                self._get_subelement(panel, "Anfa", text)
            self.gpid += 1
        return panel
    
    def _get_min_value(self, step: int, max_vp: int) -> int:
        return step if max_vp % step == 0 else max_vp % step

    def _get_subelement(self, panel_element: ET.Element, name: str, text: str) -> ET.Element:
        element = ET.SubElement(
            panel_element,
            "VASSAL.build.widget.PieceSlot",
            attrib={
                "entryName": name,
                "gpid": str(self.gpid),
                "height": "64",
                "width": "75"
            },
        )
        if(text is not None):
            element.text = text
        return element
