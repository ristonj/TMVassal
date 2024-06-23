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
            .lower()
        if replace_minus:
            retval = retval.replace("-", "minus")
        return retval