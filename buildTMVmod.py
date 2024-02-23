import xml.etree.ElementTree as ET

def buildInfantryNodes(xml_file: str, gpid: int) -> tuple[int, list[ET.Element]]:
    tree = ET.parse(xml_file)
    root = tree.getroot()
    infantryParent = root.find("./tokenGroupParent").attrib["name"]
    infantryChild = root.find("./tokenGroupChild").attrib["name"]
    infantryTemplates = root.find("./powerInfantry")
    infantryPowers = infantryTemplates.find("./powers")
    infantryGroups = []
    xStart = infantryTemplates.attrib["xStart"]
    xInc = infantryTemplates.attrib["xInc"]
    yCurrent = infantryTemplates.attrib["yStart"]
    yInc = infantryTemplates.attrib["yInc"]
    for infantryPowerTokens in infantryPowers.findall("./power"):
        xCurrent = xStart
        for token in infantryPowerTokens.findall("./token"):
            tokenName = f"{0} {1} infantry".format(token.attrib["strength"], infantryPowerTokens.attrib["name"])
            infantryGroup = ET.Element(
                infantryParent,
                attrib={
                    "name": tokenName,
                    "owningBoard": root.find("owningBoard").attrib["name"],
                    "useGridLocation": "false",
                    "x": xCurrent,
                    "y": yCurrent
                }
            )
            for _ in range(int(token.attrib["numTokens"])):
                node = ET.SubElement(
                    infantryGroup,
                    infantryChild,
                    attrib={
                        "entryName": tokenName,
                        "gpid": gpid,
                        "height": root.find("./tokenDimensions/dimension[@type]").attrib["height"],
                        "width": root.find("./tokenDimensions/dimension[@type]").attrib["width"]
                    },
                    text=infantryTemplates.find("./tokenText").text.format(
                            x=xCurrent,
                            y=yCurrent,
                            prototype="Land\\/Naval Units",
                            backCommand="Militia",
                            frontCommand="Regular",
                            frontImage=infantryPowerTokens.attrib["name"].replace(" ", "").lower() + token.attrib["strength"] + "reg.png",
                            backImage=infantryPowerTokens.attrib["name"].replace(" ", "").lower() + token.attrib["strength"] + "mil.png",
                            layerNames="1 Nasrid regular,1 Nasrid militia"
                    )
                )
                infantryGroups.append(node)
                gpid += 1
                xCurrent += xInc
        yCurrent += yInc
        xCurrent = xStart
    return gpid, infantryGroups

tree = ET.parse("BaseTantoMonta.xml")
root = tree.getroot()
nextID, infantryNodes = buildInfantryNodes("tokens.xml", 0)
infantryTree = ET.Element("top")
map(lambda x: infantryTree.append(x), infantryNodes)
# element = root.find("./VASSAL.build.module.Map[@mapName='Land/Naval Units']")
# print(element.attrib["mapName"])
infantryTree.write("build.xml")