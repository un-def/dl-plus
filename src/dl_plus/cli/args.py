from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from argparse import _ActionsContainer as _ArgumentParserLike


class Arg:

    __slots__ = ('args', 'kwargs')

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def add_to_parser(self, parser: _ArgumentParserLike):
        return parser.add_argument(*self.args, **self.kwargs)


class ArgGroup:

    __slots__ = ('arguments', 'title', 'description')

    def __init__(
        self, *arguments: Arg, title: str, description: str | None = None,
    ):
        self.arguments = arguments
        self.title = title
        self.description = description

    def add_to_parser(self, parser: _ArgumentParserLike):
        group = parser.add_argument_group(
            title=self.title, description=self.description)
        for arg in self.arguments:
            arg.add_to_parser(group)


class ExclusiveArgGroup:

    __slots__ = ('arguments', 'title', 'description', 'required')

    def __init__(
        self, *arguments: Arg, required: bool = False,
        title: str | None = None, description: str | None = None,
    ):
        self.arguments = arguments
        self.required = required
        self.title = title
        self.description = description

    def add_to_parser(self, parser: _ArgumentParserLike):
        if self.title:
            parent = parser.add_argument_group(
                title=self.title, description=self.description)
        else:
            parent = parser
        group = parent.add_mutually_exclusive_group(required=self.required)
        for arg in self.arguments:
            arg.add_to_parser(group)


dlp_config = ExclusiveArgGroup(
    Arg('--dlp-config', metavar='PATH', help='dl-plus config path.'),
    Arg(
        '--no-dlp-config', action='store_true',
        help='Do not read dl-plus config.',
    ),
    title='config options',
)
