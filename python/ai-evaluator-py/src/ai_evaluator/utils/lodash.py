"""lodash.com similar utility functions."""

from typing import Any


def noop(obj: Any) -> Any:  # noqa: ANN401 "Dynamically typed expressions are disallowed"
    """
    Do nothing.

    Args:
        obj: The object to return.

    Returns
    -------
        The input object.
    """
    pass  # pylint: disable=unnecessary-pass


def identity(x: Any) -> Any:  # noqa: ANN401 "Dynamically typed expressions are disallowed"
    """Return the same provided object/value.

    :param x: Any input
    :return: The same input
    """
    return x
