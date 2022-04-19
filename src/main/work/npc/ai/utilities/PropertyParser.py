import os
from typing import Optional

import logging
import lrparsing
from lrparsing import Prio, Ref, THIS, Token


class PropertyParser:
    class Parser(lrparsing.Grammar):
        class T(lrparsing.TokenRegistry):
            subStart = Token("${")
            subEnd = Token("}")
            colon = Token(":")
            anything = Token(re=r"[^${}:]+")
        #
        # Grammar rules.
        #
        property = Ref("property")                # Forward reference

        replacement = T.anything | T.anything + T.colon | T.anything + T.colon + property
        substitution = T.subStart + replacement + T.subEnd
        colonAnything = T.colon | T.anything
        colonized = lrparsing.Some(colonAnything)
        property = Prio(
            colonized,
            substitution,
            colonized + substitution,
            substitution << THIS,
            colonized + substitution << THIS
        )

        START = property                  # Where the grammar must start
        COMMENTS = (                      # Allow C and Python comments
            Token(re="/[*](?:[^*]|[*][^/])*[*]/")
        )

    @classmethod
    def parse(cls, prop: str) -> Optional[str]:
        try:
            tree = cls.Parser.parse(prop)
            return cls.__generate(tree)
        except lrparsing.ParseError as e:
            logging.error(f"Invalid environment replacement syntax in '{prop}'")
            raise RuntimeError(str(e))

    @classmethod
    def __generate(cls, node: tuple):
        nodeName = node[0].name
        if nodeName in ["START", "property", "colonized", "colonAnything"]:
            return "".join(filter(None, [cls.__generate(n) for n in node[1:]]))
        elif nodeName in ["T.colon", "T.anything"]:
            return node[1]
        elif nodeName == "substitution":
            return cls.__generate(node[2])
        elif nodeName == "replacement":
            envName = node[1][1]
            if len(node) == 3:
                default = None
            elif len(node) == 4:
                default = cls.__generate(node[3])
            else:
                default = None

            value = os.environ.get(envName)
            return value if value else default
        else:
            raise RuntimeError(f"Unrecognized node {cls.Parser.repr_parse_tree(node)}")

