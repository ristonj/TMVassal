import xml.etree.ElementTree as ET

from models.tokenCommonData import TokenCommonData
from . import utils

class PowerCardBuilder:
    def __init__(self, gpid: int, tokenCommonData: TokenCommonData):
        self.gpid = gpid
        self.tokenCommonData = tokenCommonData

    def buildPowerCards(self, power_card_file: str) -> tuple[list[ET.Element], list[ET.Element]]:
        stack_nodes = []
        space_nodes = []
        power_card_tree = ET.parse(power_card_file)
        owningBoard = power_card_tree.find("./owningBoard").attrib["name"]
        for power in power_card_tree.findall("./powers/power"):
            powerName = power.attrib["name"]
            stack_nodes.append(self._get_settlement(
                power.find("./settlementStack"),
                powerName,
                owningBoard,
                power_card_tree.find("./settlementTokenText").text
            ))
            
            stack_nodes.append(self._get_piracy_stack(
                power.find("./piracyStack"),
                powerName,
                owningBoard,
                power_card_tree.find("./piracyTokenText").text
            ))

            homeKeys = power.find("./homeKeys")
            if(homeKeys is not None):
                stack_nodes.extend(self._add_home_keys(
                    homeKeys,
                    powerName,
                    owningBoard,
                    power_card_tree.find("./homeKeyTokenText").text
                ))

            otherKeys = power.find("./otherKeys")
            stack_nodes.extend(self._add_other_keys(
                otherKeys,
                powerName,
                owningBoard,
                power_card_tree.find("./spainKeyTokenText").text,
                power_card_tree.find("./otherKeyTokenText").text
            ))
            
            corsair_node = power.find("./corsairTrack")
            if(corsair_node is not None):
                track, corsair_token = self._get_track(corsair_node, "Corsair VP", 12, owningBoard)
                space_nodes.append(track)
                stack_nodes.append(corsair_token)
            
            nasrid_resistance_node = power.find("./nasridResistanceTrack")
            if(nasrid_resistance_node is not None):
                track, nasrid_resistance_token = self._get_track(nasrid_resistance_node, "Nasrid Resistance VP", -3, owningBoard, True)
                space_nodes.append(track)
                stack_nodes.append(nasrid_resistance_token)
        return space_nodes, stack_nodes
    
    def _add_home_keys(self, homeKeys: ET.Element, power_name: str, owning_board: str, text: str) -> list[ET.Element]:
        stack_nodes = []
        x = int(homeKeys.attrib["x"])
        for homeKey in homeKeys.findall("./homeKey"):
            stack_nodes.append(self._get_home_key(
                homeKey.attrib["name"],
                power_name,
                owning_board,
                text,
                str(x),
                homeKeys.attrib["y"]
            ))
            x += int(homeKeys.attrib["xInc"])
        return stack_nodes
    
    def _add_other_keys(
            self,
            otherKeys: ET.Element,
            power_name: str,
            owning_board: str,
            spain_text: str,
            other_text: str) -> list[ET.Element]:
        stack_nodes = []
        numOtherKeys = int(otherKeys.attrib["numTokens"])
        x = int(otherKeys.attrib["x"])
        xInc = int(otherKeys.attrib["xInc"])
        for _ in range(numOtherKeys):
            if power_name.lower() == "spain":
                tokenText = spain_text
            else:
                tokenText = other_text
            stack_nodes.append(self._get_other_key(
                power_name,
                otherKeys.attrib["backPower"] if "backPower" in otherKeys.attrib else None,
                owning_board,
                tokenText,
                str(x),
                otherKeys.attrib["y"]
            ))
            x += xInc
        return stack_nodes

    def _get_track(
            self,
            node: ET.Element,
            name: str,
            end_of_track_vp: int,
            owning_board: str,
            start_on_right: bool = False) -> tuple[ET.Element, ET.Element]:
        track_node, track_region = utils.get_region_grid(name, node.attrib["path"])
        if end_of_track_vp < 0:
            spaces = list(range(-1, end_of_track_vp - 1, -1))
        else:
            spaces = list(range(0, end_of_track_vp + 1))
        for i in spaces:
            ET.SubElement(
                track_region,
                "VASSAL.build.module.map.boardPicker.board.Region",
                attrib={
                    "name": node.attrib["zeroPrefix"] + " " + str(i) if "zeroPrefix" in node.attrib and i == 0 else str(i),
                    "originx": str(int(node.attrib["xStart"]) + abs(i if end_of_track_vp >= 0 else i + 1) * int(node.attrib["xInc"])),
                    "originy": node.attrib["yStart"]
                }
            )
        if start_on_right:
            x = str(int(node.attrib["xStart"]) + abs(end_of_track_vp) * int(node.attrib["xInc"]))
            ET.SubElement(
                track_region,
                "VASSAL.build.module.map.boardPicker.board.Region",
                attrib={
                    "name": node.attrib["zeroPrefix"] + " 0" if "zeroPrefix" in node.attrib else "0",
                    "originx": x,
                    "originy": node.attrib["yStart"]
                }
            )
        else:
            x = node.attrib["xStart"]
        token_node, self.gpid = self.tokenCommonData.add_at_start_stack(
            tokenName=name,
            owningBoard=owning_board,
            x=x,
            y=node.attrib["yStart"],
            text=node.text,
            name=name,
            image=node.attrib["image"],
            gpid=self.gpid
        )
        return track_node, token_node
    
    def _get_home_key(self, home_key_name: str, powerName: str, owningBoard: str, home_key_token_text: str, x: str, y: str):
        home_key_stack_node, self.gpid = self.tokenCommonData.add_at_start_stack(
            gpid=self.gpid,
            tokenName=home_key_name,
            owningBoard=owningBoard,
            x=x,
            y=y,
            text=home_key_token_text,
            frontImage=f"{powerName.replace('. ', '').lower()}{home_key_name.lower()}.png",
            keyName=home_key_name,
            power=powerName
        )
        return home_key_stack_node
    
    def _get_other_key(self, powerName: str, backPower: str, owningBoard: str, other_key_token_text: str, x: str, y: str) -> ET.Element:
        other_key_stack_node, self.gpid = self.tokenCommonData.add_at_start_stack(
            gpid=self.gpid,
            tokenName=f"{powerName} SCM",
            owningBoard=owningBoard,
            x=x,
            y=y,
            text=other_key_token_text,
            frontImage=f"{powerName.replace('. ', '').lower()}square.png",
            backImage=f"{backPower.lower()}square.png" if backPower is not None else "",
            power=powerName,
            backPower=backPower
        )
        return other_key_stack_node
    
    def _get_piracy_stack(self, piracy_stack: ET.Element, powerName: str, owningBoard: str, piracy_token_text: str) -> ET.Element:
        piracy_stack_node, self.gpid = self.tokenCommonData.add_at_start_stack(
            gpid=self.gpid,
            tokenName=f"{powerName} Piracy",
            owningBoard=owningBoard,
            x=piracy_stack.attrib["x"],
            y=piracy_stack.attrib["y"],
            text=piracy_token_text,
            num_tokens=int(piracy_stack.attrib["numTokens"]),
            power=powerName.lower(),
        )
        return piracy_stack_node
    
    def _get_settlement(self, settlement_stack: ET.Element, powerName: str, owningBoard: str, settlement_token_text: str) -> ET.Element:
        settlement_stack_node, self.gpid = self.tokenCommonData.add_at_start_stack(
            gpid=self.gpid,
            tokenName=f"{powerName} Settlement",
            owningBoard=owningBoard,
            x=settlement_stack.attrib["x"],
            y=settlement_stack.attrib["y"],
            text=settlement_token_text,
            num_tokens=int(settlement_stack.attrib["numTokens"]),
            power=powerName.lower(),
        )
        return settlement_stack_node