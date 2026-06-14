"""Types used by the info system and associated scripts and generated modules.

This is a separate module to avoid circular imports.

"""


from __future__        import annotations
from typing            import NotRequired, TypedDict
from typing_extensions import TypeAlias


class InfoNode(TypedDict):
    """A node in the info documentation menu.

    The info documents are arranged in a tree of topics. Both branch nodes
    and leaf nodes can be document endpoints, but branch nodes can also
    be intermediates without an associated document. The children of
    branch nodes are subtopics. Aliasing can occur making this formally
    a DAG, but in this representation it remains a tree.

    Each endpoint node maps to a file in the frplib.data/playground_repl directory
    in the package. Labels for the nodes are stored in the keys of the
    dictionaries that structure the tree. A short descriptive text
    can optionally be included and may be displayed at the option of the
    traverser.

    Endpoints (leaf and branch nodes both) are marked by a non-missing filepath field

    """
    filepath: NotRequired[list[str]]  # Associated file path relative to frplib.data/playground_help
    description: NotRequired[str]     # Optional short descriptive text for the node
    subtopics: InfoTree | None        # Child nodes of a branch node, or None at a leaf

InfoTree: TypeAlias = dict[str, InfoNode]
