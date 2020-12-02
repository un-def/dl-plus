class Arg:

    __slots__ = ('args', 'kwargs')

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def add_to_parser(self, parser):
        return parser.add_argument(*self.args, **self.kwargs)


class ExclusiveArgGroup:

    __slots__ = ('arguments', 'required')

    def __init__(self, *arguments, required=False):
        self.arguments = arguments
        self.required = required

    def add_to_parser(self, parser):
        group = parser.add_mutually_exclusive_group(required=self.required)
        for arg in self.arguments:
            arg.add_to_parser(group)


dlp_config = ExclusiveArgGroup(
    Arg('--dlp-config', metavar='PATH', help='dl-plus config path.'),
    Arg(
        '--no-dlp-config', action='store_true',
        help='Do not read dl-plus config.',
    ),
)

backend = Arg(
    '--backend',
    metavar='BACKEND',
    help='youtube-dl backend.',
)
