import xml.etree.ElementTree as ET

from models.token_common_data import TokenCommonData
from models.unit_token_stack import UnitTokenStack

class UnitBuilder:
    def __init__(self, gpid: int, tokenCommonData: TokenCommonData):
        self.gpid = gpid
        self.tokenCommonData = tokenCommonData

    def add_at_start_stack(self, root: ET.Element, token_type: ET.Element, unit_token_stack: UnitTokenStack):
        token_name = token_type.attrib["nameTemplate"].format(
            strength=unit_token_stack.strength,
            power=unit_token_stack.powerName,
            name=unit_token_stack.name)
        group, self.gpid = self.tokenCommonData.add_at_start_stack(
            gpid=self.gpid,
            token_name=token_name,
            owning_board=root.find("owningBoard").attrib["name"],
            text=root.find(f"./tokenTextEntries/tokenText[@name='{token_type.attrib['tokenText']}']").text,
            num_tokens=unit_token_stack.numTokens,
            x=unit_token_stack.xCurrent,
            y=unit_token_stack.yCurrent,
            prototype="Land\\/Naval Units",
            backCommand=self._getOptionalAttribute(token_type, "backCommand"),
            frontCommand=self._getOptionalAttribute(token_type, "frontCommand"),
            frontImage=token_type.attrib["frontImage"].format(
                power=unit_token_stack.powerName.replace(" ", "").lower(),
                strength=unit_token_stack.strength.lower(),
                name=unit_token_stack.name.lower()
            ),
            backImage=self._getOptionalAttribute(token_type, "backImage").format(
                power=unit_token_stack.powerName.replace(" ", "").lower(),
                strength=unit_token_stack.strength.lower()
            ),
            layerNames=self._getOptionalAttribute(token_type, "layers").format(
                power=unit_token_stack.powerName,
                strength=unit_token_stack.strength
            ),
            name=token_name
        )
        return group

    def buildTokens(self, xml_file: str) -> list[ET.Element]:
        tree = ET.parse(xml_file)
        root = tree.getroot()
        powers = root.find("./powers")
        groups = []
        for tokens in powers.findall("./power"):
            xCurrent = tokens.attrib["xStart"]
            yCurrent = tokens.attrib["yStart"]
            for token in tokens.findall("./token"):
                tokenType = root.find(f"./tokenTypes/tokenType[@name='{token.attrib['type']}']")
                if token.attrib["numTokens"] == "0":
                    xCurrent = str(int(xCurrent) + int(tokenType.attrib["xInc"]))
                    continue
                groups.append(
                    self.add_at_start_stack(
                        root=root,
                        token_type=tokenType,
                        unit_token_stack=UnitTokenStack(
                            xCurrent=xCurrent,
                            yCurrent=yCurrent,
                            numTokens=int(token.attrib["numTokens"]),
                            strength=self._getOptionalAttribute(token, "strength"),
                            powerName=tokens.attrib["name"],
                            name=self._getOptionalAttribute(token, "name")
                        )
                    )
                )
                xCurrent = str(int(xCurrent) + int(tokenType.attrib["xInc"]))
        return groups
    
    def _getOptionalAttribute(self, element: ET.Element, key: str) -> str:
        return element.attrib[key] if key in element.attrib.keys() else ""