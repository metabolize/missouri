import typing as t
from contextlib import contextmanager


if t.TYPE_CHECKING:  # pragma: no cover
    from _typeshed import FileDescriptorOrPath, SupportsRead, SupportsWrite

Readable = t.Union["FileDescriptorOrPath", "SupportsRead[str]"]
Writable = t.Union["FileDescriptorOrPath", "SupportsWrite[str]"]


@contextmanager
def ensure_text_file_open(
    path_or_fp: t.Union[Readable, Writable], mode: t.Literal["r", "w"]
) -> t.Generator[t.IO[str], None, None]:
    import io

    if isinstance(path_or_fp, str):
        with open(path_or_fp, mode) as f:
            yield f
    elif isinstance(path_or_fp, io.IOBase) or (
        hasattr(path_or_fp, "read") and hasattr(path_or_fp, "seek")
    ):
        yield t.cast(t.TextIO, path_or_fp)
        if hasattr(path_or_fp, "flush"):
            path_or_fp.flush()
    else:
        raise ValueError("Object does not appear to be a path or a file-like object")
