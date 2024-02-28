import os
import xml.etree.ElementTree as ET
import zipfile

from models.tokenCommonData import TokenCommonData

def buildTokens(xml_file: str, gpid: int) -> tuple[int, list[ET.Element]]:
    tree = ET.parse(xml_file)
    root = tree.getroot()
    powers = root.find("./powers")
    groups = []
    tokenCommonData = getTokenCommonData(root)
    yCurrent = tokenCommonData.yStart
    for tokens in powers.findall("./power"):
        xCurrent = tokenCommonData.xStart
        for token in tokens.findall("./token"):
            tokenType = root.find("./tokenTypes/tokenType[@name='{0}']".format(token.attrib["type"]))
            powerName = tokens.attrib["name"]
            strength = ""
            if "strength" in token.attrib.keys():
                strength = token.attrib["strength"]
            tokenName = tokenType.attrib["nameTemplate"].format(strength=strength, power=powerName)
            group = ET.Element(
                tokenCommonData.parent,
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
                    group,
                    tokenCommonData.child,
                    attrib={
                        "entryName": tokenName,
                        "gpid": str(gpid),
                        "height": root.find("./tokenDimensions/dimension[@type='{0}']".format(tokenType.attrib["dimension"])).attrib["height"],
                        "width": root.find("./tokenDimensions/dimension[@type='{0}']".format(tokenType.attrib["dimension"])).attrib["width"]
                    }
                )
                node.text=root.find("./tokenText").text.format(
                            x=xCurrent,
                            y=yCurrent,
                            prototype="Land\\/Naval Units",
                            backCommand=tokenType.attrib["backCommand"],
                            frontCommand=tokenType.attrib["frontCommand"],
                            frontImage=tokenType.attrib["frontImage"].format(power=powerName.replace(" ", "").lower(), strength=strength),
                            backImage=tokenType.attrib["backImage"].format(power=powerName.replace(" ", "").lower(), strength=strength),
                            layerNames=tokenType.attrib["layers"].format(power=powerName, strength=strength),
                            name=tokenName
                )
                print(node.text)
                gpid += 1
            groups.append(group)
            xCurrent = str(int(xCurrent) + int(tokenType.attrib["xInc"]))
        yCurrent = str(int(yCurrent) + int(tokens.attrib["yInc"]))
        xCurrent = tokenCommonData.xStart
    return gpid, groups

def createVmod():
    imagePath = "./images"
    with zipfile.ZipFile("tmwip.vmod", "w") as vmodZip:
        vmodZip.write("buildFile.xml")
        vmodZip.write("moduledata")
        for root, dirs, files in os.walk(imagePath):
            for file in files:
                vmodZip.write(os.path.join(root, file), 
                        os.path.relpath(os.path.join(root, file), 
                                        os.path.join(imagePath, '..')))

def getTokenCommonData(root):
    powers=root.find("./powers")
    return TokenCommonData(
        parent=root.find("./tokenGroupParent").attrib["name"],
        child=root.find("./tokenGroupChild").attrib["name"],
        tokenText=root.find("./tokenText").text,
        xStart=powers.attrib["xStart"],
        yStart=powers.attrib["yStart"]
    )

def main():
    tree = ET.parse("BaseTantoMonta.xml")
    root = tree.getroot()
    initGPID = int(root.attrib["nextPieceSlotId"])
    nextID, infantryNodes = buildTokens("tokens.xml", initGPID)
    root.attrib["nextPieceSlotId"] = str(nextID)
    infantryRoot = root.find("./VASSAL.build.module.Map[@mapName='Land/Naval Units']")
    for node in infantryNodes:
        infantryRoot.append(node)
    ET.indent(tree, space="\t", level=0)
    tree.write("buildFile.xml", encoding="utf-8")
    createVmod()

if __name__ == "__main__":
    main()