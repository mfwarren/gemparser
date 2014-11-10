
__version__ = '0.1'

import re


GEM_NAME = "[a-zA-Z0-9\-_\.]+"
QUOTED_GEM_NAME = r"(?:(?P<gq>[\"'])(?P<name>%s)(?P=gq)|%%q<((?P=name)%s)>)" % (GEM_NAME, GEM_NAME)

MATCHER = r"(?:=|!=|>|<|>=|<=|~>)"
VERSION = r"[0-9]+(?:\.[a-zA-Z0-9]+)*"
REQUIREMENT = r"[ \t]*(?:%s[ \t]*)?%s[ \t]*" % (MATCHER, VERSION)
REQUIREMENT_LIST = r"(?P<qr1>[\"'])(?P<req1>%s)(?P=qr1)(?:[ \t]*,[ \t]*(?P<qr2>[\"'])(?P<req2>%s)(?P=qr2))?" % (REQUIREMENT, REQUIREMENT)
REQUIREMENTS = r"(?:%s|\[[ \t]*%s[ \t]*\])" % (REQUIREMENT_LIST, REQUIREMENT_LIST)

KEY = r"(?::\w+|:?\"\w+\"|:?'\w+')"
SYMBOL = r"(?::\w+|:\"[^\"#]+\"|:'[^']+')"
STRING = r"(?:\"[^\"#]*\"|'[^']*')"
BOOLEAN = r"(?:true|false)"
NIL = r"nil"
ELEMENT = r"(?:%s|%s)" % (SYMBOL, STRING)
ARRAY = r"\[(?:%s(?:[ \t]*,[ \t]*%s)*)?\]" % (ELEMENT, ELEMENT)
VALUE = r"(?:%s|%s|%s|%s|)" % (BOOLEAN, NIL, ELEMENT, ARRAY)
PAIR = r"(?:(%s)[ \t]*=>[ \t]*(%s)|(\w+):[ \t]+(%s))" % (KEY, VALUE, VALUE)
OPTIONS = r"%s(?:[ \t]*,[ \t]*%s)*" % (PAIR, PAIR)
COMMENT = r"(#[^\n]*)?"

GEM_CALL = r"^[ \t]*gem\(?[ \t]*%s(?:[ \t]*,[ \t]*%s)?(?:[ \t]*,[ \t]*(?P<opts>%s))?[ \t]*\)?[ \t]*%s$" % (QUOTED_GEM_NAME, REQUIREMENT_LIST, OPTIONS, COMMENT)

# SYMBOLS = /#{SYMBOL}([ \t]*,[ \t]*#{SYMBOL})*/
# GROUP_CALL = /^(?<i1>[ \t]*)group\(?[ \t]*(?<grps>#{SYMBOLS})[ \t]*\)?[ \t]+do[ \t]*?\n(?<blk>.*?)\n^\k<i1>end[ \t]*$/m
#
# GIT_CALL = /^(?<i1>[ \t]*)git[ \(][^\n]*?do[ \t]*?\n(?<blk>.*?)\n^\k<i1>end[ \t]*$/m
#
# PATH_CALL = /^(?<i1>[ \t]*)path[ \(][^\n]*?do[ \t]*?\n(?<blk>.*?)\n^\k<i1>end[ \t]*$/m
#
# GEMSPEC_CALL = /^[ \t]*gemspec(?:\(?[ \t]*(?<opts>#{OPTIONS}))?[ \t]*\)?[ \t]*$/
#
# ADD_DEPENDENCY_CALL = /^[ \t]*\w+\.add(?<type>_runtime|_development)?_dependency\(?[ \t]*#{QUOTED_GEM_NAME}(?:[ \t]*,[ \t]*#{REQUIREMENTS})?[ \t]*\)?[ \t]*#{COMMENT}$/


class Parser:
    @classmethod
    def value(cls, string):
        if re.match(ARRAY, string):
            array = cls.values(re.sub(r'[\[\]]', '', string))
            return [i.strip(":") for i in array]
        elif re.match(SYMBOL, string):
            return re.sub(r'[:"\']', '', string)
        elif re.match(STRING, string):
            return re.sub(r'["\']', '', string)
        elif re.match(BOOLEAN, string):
            return string == 'true'
        elif re.match(NIL, string):
            return None

    @classmethod
    def values(cls, string):
        arr = string.strip().split(",")
        return [cls.value(i.strip()) for i in arr]


class Dependency:
    def __init__(self, name, reqs, opts=None):
        self.name = name
        self.requirements = [i for i in reqs if i is not None]
        self.options = opts

        if type(opts) is dict and 'type' in opts:
            self.type = Parser.value(opts['type'])
        else:
            self.type = 'runtime'

        if type(opts) is dict and 'group' in opts:
            self.groups = Parser.value(opts['group'])
            if type(self.groups) is str:
                self.groups = [self.groups]
        else:
            self.groups = ['default']

    def __str__(self):
        return "%s - %s - %s" % (self.name, self.requirements, self.options)


class Gemfile:
    _dependencies = []
    _gems = []

    def __init__(self, content):
        self.content = content

    @property
    def dependencies(self):
        return [i for i in self._gem_matches() if i is not None]

    def _gem_matches(self):
        return self._matches(GEM_CALL)

    def _matches(self, regex):
        return [self._dependency(match) for match in re.finditer(regex, self.content, re.MULTILINE)]

    def _dependency(self, match):
        opts = self._parse_options(OPTIONS, match.group('opts'))
        return Dependency(match.group('name'), (match.group('req1'), match.group('req2')), opts)

    def _parse_options(self, pattern, opts):
        if opts is None:
            return None
        opts = re.search(pattern, opts).groups()
        opts = dict(zip(opts[0::2], opts[1::2]))
        opts.pop(None, None)
        opts = {k.strip(':'): opts[k] for k in opts}
        return opts
