import sys


# Formatting strings
FORMAT_2 = "{} {}"
FORMAT_3 = "{} {} {}"
FORMAT_4 = "{} {} {} {}"


def addVertex(g: dict, a) -> bool:
    """
    Add a vertex `a` to the graph given by `g`

    - -
    Parameters:
    - `g`: the graph to add the edge to
    - `a`: the node to add
    - -
    Returns: 
    - `boolean`: whether or not the vertex is already in the graph
    """

    if a in g:
        return False

    g[a] = []
    return True


def addEdge(g: dict, a, b) -> bool:
    """
    Add a directed edge between two nodes (addresses) to the digraph given by `g`

    - -
    Parameters:
    - `g`: the graph to add the edge to
    - `a`: the first node of the edge
    - `b`: the second node of the edge
    - -
    Returns: 
    - `boolean`: whether or not the edge is already in the graph
    """

    if a not in g:
        g[a] = []
    if b not in g:
        g[b] = []

    if b in g[a]:
        return False

    g[a].append(b)
    return True


def checkSiblings(a: str, b: str):
    """
    Check if the subnetworks `a` and `b` are in the same network

    - -
    Parameters:
    - `a`: the first network
    - `b`: the second network
    - -
    Returns: 
    - `boolean`: whether or not `a` and `b` are in the same network
    """

    ta = '.'.join(a.split('.')[:3])
    tb = '.'.join(b.split('.')[:3])
    return ta == tb


def updateGraph(g: dict):
    """
    Update the graph `g` and add any new vertices/edges

    - -
    Parameters:
    - `g`: the graph to update
    - -
    Returns: 
    - `boolean`: whether or not `g` changed
    """

    changed = False

    for i in g:
        for j in g:
            if i != j:
                if checkSiblings(i, j):
                    changed = addEdge(g, i, j) or changed

    return changed


# def bfs(g:dict, a):
#     """
#     Perform a Breadth-First Search (BFS) using `a` as the root and return the traversal

#     - -
#     Parameters:
#     - `g`: the graph to update
#     - `a`: the root to begin the BFS with
#     - -
#     Returns:
#     - `list[str]`: the BFS traversal from `a`
#     """

#     #! does some weird fucked up shit to the path and isn't actually the shortest :/

#     marked = set()
#     path = []
#     q = []
#     q.append(a)
#     marked.add(a)
#     while q:
#         v = q.pop(0)
#         path.append(v)
#         for n in g[v]:
#             if n not in marked:
#                 marked.add(n)
#                 q.append(n)
#     return path


def pathTo(g: dict, a, b):
    """
    Find the path from `a` to `b` in the digraph `g`.\n
    This uses a modified version of Breadth-First Search (BFS) to calculate the shortest path from the node `a`
    to the node `b`.

    - -
    Parameters:
    - `g`: the graph to search
    - `a`: the root to begin the BFS with
    - `b`: the node to find
    - -
    Returns: 
    - `list[str]`: the BFS traversal from `a` to `b` if there exists one, or
    - `None`: if there is no path
    """

    q = []  # queue
    visited = set()  # set of visited nodes
    q.append([a])  # start is in the queue
    visited.add(a)  # start is visited
    while q:
        path = q.pop(0)  # get the top of the queue
        n = path[-1]  # get the end of the path
        if n == b:
            return path
        for s in g[n]:  # for each node adjacent to the current one
            if s not in visited:
                visited.add(s)  # visit adj node
                npath = list(path)  # new path is a copy of current old path
                npath.append(s)  # add adj node to new path
                q.append(npath)  # add all values in new path to queue
    return None


def strPathTo(g: dict, a, b):
    """
    Find the path from `a` to `b` in the digraph `g` and return it as a string

    - -
    Parameters:
    - `g`: the graph to search
    - `a`: the root to begin the BFS with
    - `b`: the node to find
    - -
    Returns: 
    - `str`: the BFS traversal from `a` to `b` if there exists one as a comma-separated string, or
    - `str`: an empty string if there is no path
    """

    path = pathTo(g, a, b)
    f = ""
    if path:
        for x in path:
            f += x + ","
    return f[:-1]
