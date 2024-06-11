class TokenCommonData:
    def __init__(self, parent, child):
        self.parent = parent
        self.child = child

    @staticmethod
    def get_image_name(name: str) -> str:
        return name \
            .replace(" ", "") \
            .replace("(", "") \
            .replace(")", "") \
            .replace("+", "plus") \
            .replace("-", "minus") \
            .lower()