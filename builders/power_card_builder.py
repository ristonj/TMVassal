import xml.etree.ElementTree as ET

from models.tokenCommonData import TokenCommonData

class PowerCardBuilder:
    def __init__(self, gpid: int, tokenCommonData: TokenCommonData):
        self.gpid = gpid
        self.tokenCommonData = tokenCommonData

    def buildPowerCards(self, power_card_file: str):
        stack_nodes = []
        power_card_tree = ET.parse(power_card_file)
        settlement_token_text = power_card_tree.find("./settlementTokenText").text
        piracy_token_text = power_card_tree.find("./piracyTokenText").text
        owningBoard = power_card_tree.find("./owningBoard").attrib["name"]
        for power in power_card_tree.findall("./powers/power"):
            powerName = power.attrib["name"]
            stack_nodes.append(self._get_settlement(
                power.find("./settlementStack"),
                powerName,
                owningBoard,
                settlement_token_text
            ))
            
            stack_nodes.append(self._get_piracy_stack(
                power.find("./piracyStack"),
                powerName,
                owningBoard,
                piracy_token_text
            ))
        return stack_nodes
    
    def _get_piracy_stack(self, piracy_stack: ET.Element, powerName: str, owningBoard: str, piracy_token_text: str):
        settlement_stack_node = ET.Element(
            self.tokenCommonData.parent,
            attrib={
                "name": f"{powerName} Piracy Tokens",
                "owningBoard": owningBoard,
                "useGrid": "false",
                "x": piracy_stack.attrib["x"],
                "y": piracy_stack.attrib["y"]
            }
        )
        tokenName = f"{powerName} Piracy"
        for _ in range(int(piracy_stack.attrib["numTokens"])):
            ET.SubElement(
                settlement_stack_node,
                self.tokenCommonData.child,
                attrib={
                    "entryName": tokenName,
                    "gpid": str(self.gpid),
                    "height": "64",
                    "width": "75"
                }
            ).text = \
                piracy_token_text.format(
                    owningBoard=owningBoard,
                    x=piracy_stack.attrib["x"],
                    y=piracy_stack.attrib["y"],
                    power=powerName.lower(),
                    tokenName=tokenName
                )
            self.gpid += 1
        return settlement_stack_node
    
    def _get_settlement(self, settlement_stack: ET.Element, powerName: str, owningBoard: str, settlement_token_text: str):
        settlement_stack_node = ET.Element(
            self.tokenCommonData.parent,
            attrib={
                "name": f"{powerName} Settlements",
                "owningBoard": owningBoard,
                "useGrid": "false",
                "x": settlement_stack.attrib["x"],
                "y": settlement_stack.attrib["y"]
            }
        )
        tokenName = f"{powerName} Settlement"
        for _ in range(int(settlement_stack.attrib["numTokens"])):
            ET.SubElement(
                settlement_stack_node,
                self.tokenCommonData.child,
                attrib={
                    "entryName": tokenName,
                    "gpid": str(self.gpid),
                    "height": "64",
                    "width": "75"
                }
            ).text = \
                settlement_token_text.format(
                    owningBoard=owningBoard,
                    x=settlement_stack.attrib["x"],
                    y=settlement_stack.attrib["y"],
                    power=powerName.lower(),
                    tokenName=tokenName
                )
            self.gpid += 1
        return settlement_stack_node