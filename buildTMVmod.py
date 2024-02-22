import xml.etree.ElementTree as ET

def buildInfantryNodes(xml_file: str, gpid: int) -> tuple[int, list[ET.Element]]:
    tree = ET.parse(xml_file)
    root = tree.getroot()
    infantryParent = root.find("./tokenGroupParent")["name"]
    infantryChild = root.find("./tokenGroupChild")["name"]
    infantryTemplates = root.find("./powerInfantry")
    infantryGroups = []
    for infantryTemplate in infantryTemplates:
        gpid += 1
        infantryGroup = ET.Element(
            tag=infantryParent,
            attrib={
                "name": infantryTemplate
            }
        )
    return gpid, infantryGroups

tree = ET.parse("BaseTantoMonta.xml")
root = tree.getroot()
nextID, infantryNodes = buildInfantryNodes("tokens.xml", 0)
element = root.find("./VASSAL.build.module.Map[@mapName='Land/Naval Units']")
print(element.attrib["mapName"])
# tree.write("build.xml")