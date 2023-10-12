class NotAGoodNumber(Exception):
    def __init__(self, message, *args: object) -> None:
        super().__init__(*args)
        self.message = message

    def __str__(self) -> str:
        return self.message


class NotAGoodType(Exception):
    def __init__(self, message, *args: object) -> None:
        super().__init__(*args)
        self.message = message

    def __str__(self) -> str:
        return self.message
