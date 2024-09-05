#
# Random Graphs Example Chapter 0, Section 2.3
#

__all__ = [
    'edge_kind', 'random_graph', 'node_count', 'edge_count', 'has_edge',
    'is_connected', 'is_tree', 'is_acyclic',  'is_forest',
    'connected_components', 'connected_component_count', 'connected_component_sizes',
    'path_between', 'degrees', 'degrees_ordered', 'ForEachComponent',
    'fast_edge_count', 'exact_edge_count', 'exact_is_tree',
    'adjacency_matrix', 'adjacency_list', 'show_graph',
]

import math
import os
import subprocess
import sys

from collections       import defaultdict
from collections.abc   import Iterable
from tempfile          import mkstemp
from typing            import cast, Union

from frplib.exceptions import StatisticError
from frplib.frps       import FRP, frp, is_frp
from frplib.kinds      import fast_mixture_pow, weighted_as
from frplib.statistics import (Condition, Constantly, Id, Sum,
                               condition, is_true, scalar_statistic, statistic)
from frplib.quantity   import as_quantity
from frplib.utils      import frequencies
from frplib.vec_tuples import VecTuple, as_scalar_strict, as_vec_tuple, is_vec_tuple, vec_tuple


#
# Kind/FRP Factories
#

def edge_kind(p='1/2'):
    """Returns the kind of a single edge in a random graph.

    Parameters
    ----------
    p: probability of an edge, a number between 0 and 1.

    Returns a kind of dimension 1 and size 2.

    """
    p = as_quantity(p)
    return weighted_as(0, 1, weights=[1 - p, p])

def random_graph(n, p='1/2'):
    p = as_quantity(p)
    m = (n * (n - 1)) // 2
    return frp(edge_kind(p)) ** m


#
# Helpers
#

_node_count_inverse = {(n * (n - 1)) // 2: n for n in range(32)}  # ATTN: Is memoizing actually faster here?

def _node_count(graph) -> int:
    "Returns number of nodes given a tuple representing an undirected, simple graph without loops."
    m = len(graph)  # == n * (n - 1) / 2
    n = _node_count_inverse.get(m, -1)
    if n < 0:
        #   _node_count_inverse[m] = (int(math.sqrt(8 * m + 1)) - 1) // 2  # Exact
        n = _node_count_inverse[m] = 1 + int(math.sqrt(2 * m))             # Quick: ceil(sqrt(n*(n-1))) == n
    return n

def _row_index(n: int, i: int) -> int:
    "Returns index in the tuple of the (i+1,i+2) entry of the adjacency matrix for 0 <= i < n - 1."
    return n * i - (i * (i + 1)) // 2

def _neighbors(n: int, i: int, graph: tuple[int, ...]) -> list[int]:
    "Returns zero-index nodes that are neighbors of the (zero-index) i-th node in a graph."
    # neighbors of greater index
    gt = _row_index(n, i)
    neighbors = [i + k + 1 for k in range(n - i - 1) if graph[gt + k] > 0]
    # add neighbors of lower index
    for i0 in range(i):
        ind = _row_index(n, i0) + i - i0 - 1
        if graph[ind] > 0:
            neighbors.append(i0)
    return neighbors


#
# Statistics, Statistic Factories, and Statistic Combinators
#

@scalar_statistic
def node_count(graph):
    "A statistic that returns the number of nodes in an undirected, simple graph without loops."
    return _node_count(graph)

@scalar_statistic
def edge_count(graph):
    "A statistic that returns the number of edges in an undirected, simple graph without loops."
    return Sum(graph)

def has_edge(node_i: int, node_j: int) -> Condition:
    """Returns a condition testing whether {node_i, node_j} is an edge in the given graph.

    node_i and node_j must be positive integers or a StatisticsError is raised.

    Input to the condition is a tuple giving the row-wise, upper triangle of the
    adjacency matrix for an undirected, simple graph without loops.

    """
    if node_i < 1 or node_j < 1:
        raise StatisticError('')

    if node_i == node_j:
        return Condition(Constantly(False))

    i = min(node_i, node_j) - 1  # zero-index nodes
    j = max(node_i, node_j) - 1
    k = j - i - 1                # >= 0

    def has_edge_ij(graph):
        n = _node_count(graph)

        if i >= n - 1 or j >= n:
            return False

        # Skip (n - 1) + ... + (n - i) then take kth
        ind = _row_index(n, i) + k
        return bool(graph[ind])

    has_edge_ij.__doc__ = f'A condition that tests whether edge {{{i+1}, {j+1}}} belongs to an undirected, simple graph without loops.'

    return Condition(has_edge_ij)

@condition
def is_connected(graph):
    """A condition that tests whether an undirected, simple graph without loops is connected.

    Input to the condition is a tuple giving the row-wise, upper
    triangle of the graph's adjacency matrix.

    """
    n = _node_count(graph)
    total = (n * (n + 1)) // 2
    connected = 0
    stack = [0]
    visited = [False] * n

    while len(stack) > 0:
        i = stack.pop()
        if visited[i]:
            continue
        visited[i] = True
        connected += i + 1
        # Push neighbors
        stack.extend(_neighbors(n, i, graph))
        # Check for early termination
        if connected == total:
            return True

    return connected == total

@condition
def is_tree(graph):
    """A condition that tests whether an undirected, simple graph without loops is a tree.

    Input to the condition is a tuple giving the row-wise, upper
    triangle of the graph's adjacency matrix.

    """
    n = _node_count(graph)
    return sum(graph) == n - 1 and is_true(is_connected(graph))
    pass

@condition
def is_acyclic(graph):
    """A condition that tests whether an undirected, simple graph without loops is a acyclic.

    Input to the condition is a tuple giving the row-wise, upper
    triangle of the graph's adjacency matrix.

    """
    n = _node_count(graph)
    stack = [0]
    visited = [False] * n
    parents = [-1] * n

    while True:
        while len(stack) > 0:
            i = stack.pop()
            visited[i] = True
            for ngb in _neighbors(n, i, graph):
                if ngb == parents[i]:
                    continue
                if visited[ngb]:
                    return False
                parents[ngb] = i
                stack.append(ngb)
        if not all(visited):
            stack = [visited.index(False)]
        else:
            break
    return True

@statistic
def connected_components(graph):
    """A statistic that identifies the connected components of an undirected, simple graph without loops.

    Input to the condition is a tuple giving the row-wise, upper
    triangle of the graph's adjacency matrix.

    Returns a tuple ATTN

    """
    n = _node_count(graph)
    components = [n + 1] * n   # n + 1 means unlabeled
    next_component = 1
    for i in range(n):
        neighbors = _neighbors(n, i, graph)
        # Isolated node
        if not neighbors:
            components[i] = next_component
            next_component += 1
            continue
        # Non-isolated node
        comp = min(next_component, components[i], min(components[j] for j in neighbors))
        for j in neighbors:
            components[j] = comp
        components[i] = comp
        if comp == next_component:
            next_component += 1
    return components

@scalar_statistic
def connected_component_count(graph):
    """A statistic that returns the number of connected components of an undirected, simple graph without loops.

    Input to the condition is a tuple giving the row-wise, upper
    triangle of the graph's adjacency matrix.

    """
    return max(connected_components(graph))  # type: ignore

def path_between(node_i, node_j):
    """Returns a condition testing whether there is a path between node_i and node_j in the given graph.

    node_i and node_j must be positive integers or a StatisticsError is raised.

    Input to the condition is a tuple giving the row-wise, upper triangle of the
    adjacency matrix for an undirected, simple graph without loops.

    """
    if node_i < 1 or node_j < 1:
        raise StatisticError('')

    if node_i == node_j:
        return Condition(Constantly(True))

    i = min(node_i, node_j) - 1  # zero-index nodes
    j = max(node_i, node_j) - 1

    def has_path_ij(graph):
        n = _node_count(graph)

        if i >= n - 1 or j >= n:
            return False

        queue = [i]
        start = 0
        visited = [False] * n

        while len(queue) > start:
            node = queue[start]
            if node == j:
                return True
            start += 1
            if visited[node]:
                continue
            visited[node] = True
            queue.extend(_neighbors(n, node, graph))
        return False

    has_path_ij.__doc__ = f'A condition that tests whether a path from {i+1} to {j+1} exists in an undirected, simple graph without loops.'

    return Condition(has_path_ij)
    pass

@statistic
def connected_component_sizes(comps):
    """Given an n-tuple with component labels for every node, return sorted tuple of component sizes.

    Parameter comps is a tuple with one entry per node, where each node has a label
    identifying its connected component. See statistic `connected_components`.

    The returned tuple is padded with 0s to length n, to ensure fixed dimension.

    """
    n = len(comps)
    v = cast(tuple[int, ...], frequencies(comps, counts_only=True))
    return v + (0,) * (n - len(v))

@statistic
def degrees_ordered(graph):
    "Returns degrees (# of neighbors) all nodes in the graph in increasing order."
    n = _node_count(graph)
    degs = sorted(len(_neighbors(n, i, graph)) for i in range(n))
    return as_vec_tuple(degs)

@statistic
def degrees(graph):
    "Returns degrees (# of neighbors) of every node in the graph."
    n = _node_count(graph)
    return as_vec_tuple(len(_neighbors(n, i, graph)) for i in range(n))

def ForEachComponent(stat=Id):
    """Returns a function that applies a statistic to each connected component of a graph or graph FRP.

    The returned function accepts either a graph tuple or graph FRP and returns a dictionary
    mapping the connected component label to the result of applying the statistic to the
    subgraph for that connected component.  The default statistic is the identity,
    which will give the subgraph tuple for each component.

    """
    def _subgraph_of(n, g, nodes):  # nodes zero-indexed in increasing order
        subgraph = []
        for ind in range(len(nodes) - 1):
            i = nodes[ind]
            r = _row_index(n, i)
            for j in nodes[(ind + 1):]:
                subgraph.append(g[r + j - i - 1])
        return as_vec_tuple(subgraph)

    def stat_on_components(graph):
        if is_frp(graph):
            graph = graph.value
        n = _node_count(graph)
        comps = cast(VecTuple, connected_components(graph))
        n_comps = max(comps)
        subgraphs: dict[int, list[int]] = {k: [] for k in range(1, n_comps + 1)}
        for (i, c) in enumerate(comps):
            subgraphs[c].append(i)

        return {k: stat(_subgraph_of(n, graph, sorted(subgraphs[k]))) for k in subgraphs}
    return stat_on_components

@condition
def is_forest(graph):
    "Condition that tests if graph is a forest, i.e., a collection of trees."
    component_tree = ForEachComponent(is_tree)
    subgraph_trees = component_tree(graph)
    return all(x == (1,) for x in subgraph_trees.values())


#
# Computational and Conceptual Speed-ups
#

def fast_edge_count(n, p):
    "Fast computation of the edge_count-transformed kind of random_graph(n,p)."
    m = (n * (n - 1)) // 2
    return fast_mixture_pow(Sum, edge_kind(p), m)

def exact_edge_count(n, p):
    "Exact edge_count-transformed kind of random_graph(n,p)."
    pass  # ATTN

def exact_is_tree(n):
    "Computes the exact kind of is_tree(random_graph(n))."
    # Compute n^{n-2} 2^{-binom(n,2)} efficiently and accurately
    # Of course, it's essentially negligible for n > 10 so ...
    pass


#
# Utilities
#

def adjacency_matrix(graph) -> list[list[int]]:
    "Returns a list of lists representing the binary matrix describing the edges in the given graph."
    if is_frp(graph):
        graph = graph.value
    adj = []
    n = _node_count(graph)
    for i in range(n):
        row = [0] * n
        for j in _neighbors(n, i, graph):
            row[j] = 1
        adj.append(row)
    return adj

def adjacency_list(graph, include_empty=False) -> dict[int, list[int]]:
    "Returns a dict representing the adjacency lists for the given graph."
    if is_frp(graph):
        graph = graph.value
    adj = {}
    n = _node_count(graph)
    for i in range(n):
        neighbors = _neighbors(n, i, graph)
        if include_empty or len(neighbors) > 0:
            adj[i + 1] = [j + 1 for j in neighbors]
    return adj

#
# Graph Display
#
# We generate a temporary svg file and display it with
# the default application for that type.  The layout
# is fairly rudimentary as this is just for quick
# visualization
#

def _svg_header(view_port: int) -> str:
    return f'''
<svg viewBox="0 0 {view_port} {view_port}" xmlns="http://www.w3.org/2000/svg">
  <style type="text/css">
    .nodes {{
      font: Arial 12px sans-serif;
      fill: "#5B84B1";
      stroke: "#5B84B1";
      color: "#5B84B1";
      dominant-baseline: "middle";
      text-anchor: "middle";
    }}
  </style>
'''
def _graph_svg(
        n: int,
        positions: list[tuple[float, float]],
        edges: dict[int, list[int]],
        view_port: int
) -> str:
    elements = [_svg_header(view_port)]

    for node, neighbors in edges.items():
        x1, y1 = positions[node]
        for adj in neighbors:
            x2, y2 = positions[adj]
            edge = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#FC766A" stroke-width="2" />'
            elements.append(edge)

    for node in range(n):
        x, y = positions[node]
        gnode = f'<circle cx="{x}" cy="{y}" r="25" fill="white" stroke="#5B84B1" stroke-width="3" />'
        label = f'<text x="{x}" y="{y}" class="small" text-anchor="middle" dominant-baseline="middle">{node + 1}</text>'
        elements.append(gnode)
        elements.append(label)

    elements.append('</svg>\n')  # footer
    return "\n".join(elements)

def open_file_with_default_app(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])

def _circular_graph_layout(n, R, origin) -> list[tuple[float, float]]:
    "Layout of small graph in a circle so that edges do not overlap nodes."
    return [(origin + R * math.cos(2 * math.pi * j / n), origin - R * math.sin(2 * math.pi * j / n))
            for j in range(n)]

def _coulomb_graph_layout(n, graph, edges, components, view_port):
    "Layout of graph using Coulomb forces between nodes and Hook forces on edges"
    ambient, q, hook = (0.15, 5e5, 0.1)  # Need to calibrate these carefully. These do pretty well.
    dt, anneal = (1.0, 0.999)
    tol = 0.1
    force_tol = 0.01
    max_iter = 1024

    # Initialize position in staggered circle by component
    origin = view_port / 2
    R = view_port / 4
    pos = [vec_tuple(origin + R * math.cos(2 * math.pi * j / n),
                     origin - R * math.sin(2 * math.pi * j / n))
           for j in range(n)]
    force = [vec_tuple(0.0, 0.0)] * n
    step = dt

    # Iterate using Coulomb and Hook forces towards equilibrium
    for _ in range(max_iter):
        for i in range(n):
            force[i] = -ambient * (pos[i] - origin)

        for i in range(n):
            for j in range(i + 1, n):
                dx = pos[i] - pos[j]
                dsq = as_scalar_strict(dx @ dx)
                d = math.sqrt(dsq)
                if d > tol:
                    delta = q * dx / (d * dsq)
                    force[i] += delta
                    force[j] -= delta
                else:
                    jump = vec_tuple(math.copysign(25, dx[0]), math.copysign(25, dx[1]))
                    force[i] += jump
                    force[j] -= jump

                if j in edges[i]:  # symmetric relation
                    force[i] -= hook * dx
                    force[j] += hook * dx
                    
        max_force = 0.0
        for i in range(n):
            max_force = max(max_force, math.sqrt(as_scalar_strict(force[i] @ force[i])))
            pos[i] += step * force[i]

        step *= anneal

        if max_force < force_tol or step * max_force < force_tol:
            break

    return pos

def show_graph(graph_spec: Union[Iterable, FRP]):
    """Display the graph in graphical form in a separate window.

    Note: This uses your platforms default application for opening SVG files.
    You may need to set this default to an appropriate application, e.g.,
    a modern browser like firefox or chrome.

    The layout here is rudimentary, especially for graphs with more than 20 nodes.
    This will improve in future versions.

    Returns its argument, so you can use it as a wrapper to compute and view
    simultaneously.

    Example: g = show_graph(random_graph(8))
    
    """
    if is_frp(graph_spec):
        graph = cast(tuple[int, ...], graph_spec.value)
    else:
        graph = cast(tuple[int, ...], as_vec_tuple(graph_spec))

    n = _node_count(graph)

    # Using fixed r = 25 for now, so some silly constants are here for expedience
    # ATTN: clean this up

    if n < 20:
        # Circular layout wide enough to avoid edges hitting nodes
        edges = { node: _neighbors(n, node, graph) for node in range(n) }
        # Fix node size r = 25 for now. Invert y coordinates for svg style
        view_port = 3 * n * n + 50  # R (1 - cos(2pi/n)) > r = 25 with safety R >= 1.5 n^2
        R = 1.5 * n * n
        positions = _circular_graph_layout(n, R, origin=view_port / 2)
    else:
        # A simple Coulomb-Hook layout keeping connected components close
        # This will get crowded much above 150 nodes
        # ATTN: This case is a mess, calibration tough, vectors may be off
        edges = { node: set(_neighbors(n, node, graph)) for node in range(n) }  # type: ignore
        view_port = int(175 * math.ceil(math.sqrt(n))) + 50

        comp_of: VecTuple = connected_components(graph)  # type: ignore
        num_components = max(comp_of)
        components = defaultdict(set)
        for node in range(n):
            components[comp_of[node]].add(node)

        positions = _coulomb_graph_layout(n, graph, edges, components, view_port)

    # Generate SVG and output to a temporary file
    svg = _graph_svg(n, positions, edges, view_port)

    fd, svg_file = mkstemp(suffix='.svg', prefix='graph-')
    with os.fdopen(fd, 'w') as f:
        f.write(svg)
    open_file_with_default_app(svg_file)

    return graph_spec
