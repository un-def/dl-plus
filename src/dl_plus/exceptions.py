from typing import Optional, Union


class DLPlusException(Exception):

    def __init__(self, message: Union[str, Exception, None] = None) -> None:
        if message is not None:
            message = str(message)
        self._message = message

    def __str__(self):
        if self._message is None:
            if self.__cause__:
                self._message = str(self.__cause__)
            else:
                self._message = ''
        return self._message

    @property
    def error(self) -> Optional[BaseException]:
        return self.__cause__
