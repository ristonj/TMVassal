import xml.etree.ElementTree as ET

from models.token_common_data import TokenCommonData
from . import utils

class MinorPowerBuilder:
    def __init__(self, gpid: int, token_common_data: TokenCommonData):
        self.gpid = gpid
        self.token_common_data = token_common_data
    
    def build(self, piece_file: str) -> list[ET.Element]:
        root = ET.parse(piece_file)
        minor_power_tokens = []
        for minor_power in root.findall("./power"):
            powers = [x.attrib["name"] for x in minor_power.findall("./majorAlly")]
            stack, self.gpid = self.token_common_data.add_at_start_stack(
                gpid=self.gpid,
                token_name=minor_power.attrib["name"],
                owning_board="Minor Power Influence",
                x = minor_power.attrib["x"],
                y=minor_power.attrib["y"],
                text=minor_power.find("./text").text,
                image1=f"{TokenCommonData.get_image_name(powers[0])}hexminorboard.png",
                image2=f"{TokenCommonData.get_image_name(powers[1])}hexminorboard.png",
                image3=f"{TokenCommonData.get_image_name(powers[2])}hexminorboard.png",
                power1=powers[0],
                power2=powers[1],
                power3=powers[2],
                power1_control=powers[0].replace(". ", ""),
                power2_control=powers[1].replace(". ", ""),
                power3_control=powers[2].replace(". ", ""),
            )
            minor_power_tokens.append(stack)
        return minor_power_tokens