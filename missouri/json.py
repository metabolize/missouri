# Adapted from
# https://github.com/metabolize-forks/baiji-serialization/tree/8b77f19685555e1bab03e75a433d00ce6fa4bea5
# Apache 2.0

import typing as t
import simplejson as json
from .coding import JSONDecoder, JSONEncoder
from .openlib import FileLike, ensure_text_file_open


def _dump_args(kwargs: dict) -> dict:
    if "default" in kwargs:
        raise ValueError(
            "Instead of explicitly setting default, subclass missouri.coding.JSONEncoder and pass it as encoder"
        )
    if "encoder" in kwargs:
        kwargs["default"] = kwargs["encoder"]
        del kwargs["encoder"]
    else:
        kwargs["default"] = JSONEncoder(
            encode_as_primitives=kwargs.get("encode_as_primitives", None)
        )
    if "encode_as_primitives" in kwargs:
        del kwargs["encode_as_primitives"]
    kwargs["for_json"] = True
    return kwargs


def dump(obj: t.Any, path: FileLike, *args: object, **kwargs: object) -> None:
    with ensure_text_file_open(path, "w") as f:
        json.dump(obj, f, *args, **_dump_args(kwargs))


def dumps(obj: t.Any, **kwargs: object) -> str:
    return json.dumps(obj, **_dump_args(kwargs))


def _load_args(kwargs: dict) -> dict:
    if "object_hook" in kwargs:
        raise ValueError(
            "Instead of explicitly setting object_hook, subclass missouri.coding.JSONDecoder and pass it as decoder"
        )
    if "decoder" in kwargs:
        kwargs["object_hook"] = kwargs["decoder"]
        del kwargs["decoder"]
    else:
        kwargs["object_hook"] = JSONDecoder()
    return kwargs


def load(path: FileLike, *args: object, **kwargs: object) -> t.Any:
    with ensure_text_file_open(path, "r") as f:
        return json.load(f, *args, **_load_args(kwargs))


def loads(s: str, **kwargs: object) -> t.Any:
    return json.loads(s, **_load_args(kwargs))
