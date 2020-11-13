def ichunk(iterable, n):
    """Yield n sized chunks, with tail chunk truncated.

    >>> list(ichunk([], 3))
    []
    >>> list(ichunk([1], 3))
    [[1]]
    >>> list(ichunk(range(3), 3))
    [[0, 1, 2]]
    >>> list(ichunk(range(10), 3))
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]
    """
    _iter = iter(iterable)
    while True:
        out = []
        for _ in range(n):
            try:
                out.append(next(_iter))
            except StopIteration:
                if out:
                    yield out
                return
        yield out
