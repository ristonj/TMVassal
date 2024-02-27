import os
import xml.etree.ElementTree as ET
import zipfile

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
            tokenName = "{0} {1} infantry".format(token.attrib["strength"], infantryPowerTokens.attrib["name"])
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
                        "gpid": str(gpid),
                        "height": root.find("./tokenDimensions/dimension[@type]").attrib["height"],
                        "width": root.find("./tokenDimensions/dimension[@type]").attrib["width"]
                    }
                )
                node.text=infantryTemplates.find("./tokenText").text.format(
                            x=xCurrent,
                            y=yCurrent,
                            prototype="Land\\/Naval Units",
                            backCommand="Militia",
                            frontCommand="Regular",
                            frontImage=infantryPowerTokens.attrib["name"].replace(" ", "").lower() + token.attrib["strength"] + "reg.png",
                            backImage=infantryPowerTokens.attrib["name"].replace(" ", "").lower() + token.attrib["strength"] + "mil.png",
                            layerNames="1 Nasrid regular,1 Nasrid militia",
                            name=tokenName
                )
                gpid += 1
            infantryGroups.append(infantryGroup)
            xCurrent = str(int(xCurrent) + int(xInc))
        yCurrent = str(int(yCurrent) + int(yInc))
        xCurrent = xStart
    return gpid, infantryGroups

def createVmod():
    imagePath = "./images"
    with zipfile.ZipFile("tmvip.vmod", "w") as vmodZip:
        vmodZip.write("buildFile.xml")
        vmodZip.write("moduledata")
        for root, dirs, files in os.walk(imagePath):
            for file in files:
                vmodZip.write(os.path.join(root, file), 
                        os.path.relpath(os.path.join(root, file), 
                                        os.path.join(imagePath, '..')))

def main():
    tree = ET.parse("BaseTantoMonta.xml")
    root = tree.getroot()
    initGPID = int(root.attrib["nextPieceSlotId"])
    nextID, infantryNodes = buildInfantryNodes("tokens.xml", initGPID)
    root.attrib["nextPieceSlotId"] = str(nextID)
    infantryRoot = root.find("./VASSAL.build.module.Map[@mapName='Land/Naval Units']")
    for node in infantryNodes:
        infantryRoot.append(node)
    ET.indent(tree, space="\t", level=0)
    tree.write("buildFile.xml", encoding="utf-8")
    createVmod()

if __name__ == "__main__":
    main()