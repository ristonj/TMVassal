import xml.etree.ElementTree as ET

from models.tokenCommonData import TokenCommonData

class PowerCardBuilder:
    def __init__(self, gpid: int, tokenCommonData: TokenCommonData):
        self.gpid = gpid
        self.tokenCommonData = tokenCommonData

    def buildPowerCards(self, power_card_file: str):
        stack_nodes = []
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
                x = int(homeKeys.attrib["x"])
                for homeKey in homeKeys.findall("./homeKey"):
                    stack_nodes.append(self._get_home_key(
                        homeKey.attrib["name"],
                        powerName,
                        owningBoard,
                        power_card_tree.find("./homeKeyTokenText").text,
                        str(x),
                        homeKeys.attrib["y"]
                    ))
                    x += int(homeKeys.attrib["xInc"])

            otherKeys = power.find("./otherKeys")
            numOtherKeys = int(otherKeys.attrib["numTokens"])
            x = int(otherKeys.attrib["x"])
            xInc = int(otherKeys.attrib["xInc"])
            for _ in range(numOtherKeys):
                if powerName.lower() == "spain":
                    tokenText = power_card_tree.find("./spainKeyTokenText").text
                else:
                    tokenText = power_card_tree.find("./otherKeyTokenText").text
                stack_nodes.append(self._get_other_key(
                    powerName,
                    otherKeys.attrib["backPower"] if "backPower" in otherKeys.attrib else None,
                    owningBoard,
                    tokenText,
                    str(x),
                    otherKeys.attrib["y"]
                ))
                x += xInc
        return stack_nodes
    
    def _get_home_key(self, home_key_name: str, powerName: str, owningBoard: str, home_key_token_text: str, x: str, y: str):
        home_key_stack_node = ET.Element(
            self.tokenCommonData.parent,
            attrib={
                "name": powerName,
                "owningBoard": owningBoard,
                "useGridLocation": "false",
                "x": x,
                "y": y
            }
        )
        
        ET.SubElement(
            home_key_stack_node,
            self.tokenCommonData.child,
            attrib={
                "entryName": home_key_name,
                "gpid": str(self.gpid),
                "height": "64",
                "width": "75"
            }
        ).text = \
            home_key_token_text.format(
                frontImage=f"{powerName.replace('. ', '').lower()}{home_key_name.lower()}.png",
                keyName=home_key_name,
                power=powerName,
                gpid=""
            )
        self.gpid += 1
        return home_key_stack_node
    
    def _get_other_key(self, powerName: str, backPower: str, owningBoard: str, other_key_token_text: str, x: str, y: str) -> ET.Element:
        other_key_stack_node = ET.Element(
            self.tokenCommonData.parent,
            attrib={
                "name": f"{powerName} SCM {x}",
                "owningBoard": owningBoard,
                "useGridLocation": "false",
                "x": x,
                "y": y
            }
        )
        
        ET.SubElement(
            other_key_stack_node,
            self.tokenCommonData.child,
            attrib={
                "entryName": f"{powerName} SCM",
                "gpid": str(self.gpid),
                "height": "64",
                "width": "75"
            }
        ).text = \
            other_key_token_text.format(
                frontImage=f"{powerName.replace('. ', '').lower()}square.png",
                backImage=f"{backPower.lower()}square.png" if backPower is not None else "",
                power=powerName,
                backPower=backPower,
                gpid=""
            )
        self.gpid += 1
        return other_key_stack_node
    
    def _get_piracy_stack(self, piracy_stack: ET.Element, powerName: str, owningBoard: str, piracy_token_text: str) -> ET.Element:
        settlement_stack_node = ET.Element(
            self.tokenCommonData.parent,
            attrib={
                "name": f"{powerName} Piracy Tokens",
                "owningBoard": owningBoard,
                "useGridLocation": "false",
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
                "useGridLocation": "false",
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