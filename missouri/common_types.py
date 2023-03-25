import typing as t

# Fix this when recursive types are supported.
JsonType = t.Union[None, int, float, str, bool, t.List[t.Any], t.Dict[str, t.Any]]
