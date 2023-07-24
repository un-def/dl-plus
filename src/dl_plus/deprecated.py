import warnings
from typing import Optional


__all__ = ['DLPlusDeprecationWarning', 'warn']


_filters_configured = False


def _maybe_configure_filters():
    global _filters_configured
    if not _filters_configured:
        warnings.filterwarnings('default', category=DLPlusDeprecationWarning)
        _filters_configured = True


def _calculate_stacklevel(stacklevel: Optional[int]) -> int:
    if stacklevel is None:
        stacklevel = 2
    return stacklevel + 1


class DLPlusDeprecationWarning(DeprecationWarning):
    pass


def warn(message: str, stacklevel: Optional[int] = None) -> None:
    _maybe_configure_filters()
    warnings.warn(
        message, category=DLPlusDeprecationWarning,
        stacklevel=_calculate_stacklevel(stacklevel),
    )
