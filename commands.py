import enum


class Command(enum.Enum):
    DISCONNECT_COMMAND = "!DISCONNECT"
    LOGIN_COMMAND = "!LOGIN"
    ADD_FILE_COMMAND = "!ATTACH"
