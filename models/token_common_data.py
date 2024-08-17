import xml.etree.ElementTree as ET

class TokenCommonData:
    def __init__(self, parent, child):
        self.parent = parent
        self.child = child

    @staticmethod
    def get_image_name(name: str, replace_minus: bool = True) -> str:
        retval = name \
            .replace(" ", "") \
            .replace("(", "") \
            .replace(")", "") \
            .replace("+", "plus") \
            .replace(".", "") \
            .lower()
        if replace_minus:
            retval = retval.replace("-", "minus")
        return retval
    
    def add_at_start_stack(
            self,
            **kwargs) -> tuple[ET.Element, int]:
        """Creates a VASSAL 'At Start Stack'. The needed parameters are documented below.
        All other arguments will be used to format the text argument.

        Keyword Arguments:
            gpid {int} -- The piece gpid.
            token_name {str} -- The token name.
            owning_board {str} -- The owning board.
            x {str} -- The x position of the stack.
            y {str} -- The y position of the stack.
            text {str} -- The inner text of the token as an f string.
            parent_element {xml.etree.ElementTree.Element} -- The parent element (i.e. folder) of the stack. Defaults to None for no parent.
            num_tokens {int} -- The number of tokens in the stack. Defaults to 1.

        Returns:
            tuple[ET.Element, int]: An XML node containing the at start stack, and the new gpid.
        """
        
        if("parent_element" in kwargs):
            group = ET.SubElement(
                kwargs["parent_element"],
                self.parent,
                attrib={
                    "name": kwargs["token_name"],
                    "owningBoard": kwargs["owning_board"],
                    "useGridLocation": "false",
                    "x": kwargs["x"],
                    "y": kwargs["y"]
                }
            )
        else:
            group = ET.Element(
                self.parent,
                attrib={
                    "name": kwargs["token_name"],
                    "owningBoard": kwargs["owning_board"],
                    "useGridLocation": "false",
                    "x": kwargs["x"],
                    "y": kwargs["y"]
                }
            )
        gpid = kwargs["gpid"]
        num_tokens = kwargs.get("num_tokens", 1)
        for _ in range(num_tokens):
            ET.SubElement(
                group,
                self.child,
                attrib={
                    "entryName": kwargs["token_name"],
                    "gpid": str(gpid),
                    "height": "64",
                    "width": "75"
                }
            ).text = kwargs["text"].format(**kwargs)
            gpid += 1
        return group, gpid
