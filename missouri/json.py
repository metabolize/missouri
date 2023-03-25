# Adapted from
# https://github.com/metabolize-forks/baiji-serialization/tree/8b77f19685555e1bab03e75a433d00ce6fa4bea5
# Apache 2.0

import typing as t
import simplejson as json
from .common_types import JsonType
from .numpylib import decode_numpy as _decode_numpy, encode_numpy as _encode_numpy
from .openlib import ensure_text_file_open

if t.TYPE_CHECKING:
    import numpy as np

EXTENSION = ".json"
ENCODE_AS_PRIMITIVES_BY_DEFAULT = False


def _dump_args(kwargs: dict) -> dict:
    if "default" in kwargs:
        raise ValueError(
            "Instead of explicitly setting default, subclass JSONEncoder and pass it as encoder"
        )
    if "encoder" in kwargs:
        kwargs["default"] = kwargs["encoder"]
        del kwargs["encoder"]
    else:
        kwargs["default"] = JSONEncoder(
            encode_as_primitives=kwargs.get(
                "encode_as_primitives", ENCODE_AS_PRIMITIVES_BY_DEFAULT
            )
        )
    if "encode_as_primitives" in kwargs:
        del kwargs["encode_as_primitives"]
    kwargs["for_json"] = True
    return kwargs


def dump(obj: t.Any, path: str, *args: object, **kwargs: object) -> None:
    with ensure_text_file_open(path, "w") as f:
        json.dump(obj, f, *args, **_dump_args(kwargs))


def dumps(obj: t.Any, **kwargs: object) -> str:
    return json.dumps(obj, **_dump_args(kwargs))


def _load_args(kwargs: dict) -> dict:
    if "object_hook" in kwargs:
        raise ValueError(
            "Instead of explicitly setting object_hook, subclass JSONDecoder and pass it as decoder"
        )
    if "decoder" in kwargs:
        kwargs["object_hook"] = kwargs["decoder"]
        del kwargs["decoder"]
    else:
        kwargs["object_hook"] = JSONDecoder()
    return kwargs


def load(path: str, *args: object, **kwargs: object) -> JsonType:
    with ensure_text_file_open(path, "r") as f:
        return json.load(f, *args, **_load_args(kwargs))


def loads(s: str, **kwargs: object) -> JsonType:
    return json.loads(s, **_load_args(kwargs))


class MethodListCaller:
    """
    This is an internal class that lets the JSON(En,De)coder classes
    and their subclasses easily register a list of methods to try, which
    will then be called in order until one of them succeeds.
    """

    def register(self, method, index=-1):
        if not hasattr(self, "method_list"):
            self.clear()
        if index == -1:
            index = len(self.method_list)
        self.method_list.insert(index, method)

    def clear(self) -> None:
        # be defensive if someone forgets to call super pylint: disable=attribute-defined-outside-init
        self.method_list = []

    def __call__(self, obj: t.Any) -> t.Optional[JsonType]:
        """
        Call the methods in method_list until one of them returns something other than None
        and return that as the result of the call.
        """
        try:
            return next(
                filter(lambda x: x is not None, (f(obj) for f in self.method_list))
            )
        except StopIteration:
            return self.default(obj)

    def default(self, x: t.Any) -> t.Optional[JsonType]:
        """
        If none of the methods returned something, then return this default
        """
        return x


class JSONDecoder(MethodListCaller):
    """
    Instances may be passed to simplejson as object_hook to decode json objects.
    The decoders will be called in order. The first one to return something other
    than None wins. The decoders will be given a dict to parse, something like:

        {
            "__ndarray__": [
                    [859.0, 859.0],
                    [217.0, 106.0],
                    [302.0, 140.0]
                ],
            "dtype": "float32",
            "shape": [3, 2]
        }

    Note that for object_hook, if we want to do nothing, we return the dict unchanged
    and the json is decoded as a plain old dict; this behavior is the default of
    MethodListCaller.
    """

    def __init__(self) -> None:
        self.register(self.decode_numpy)
        self.register(self.decode)

    def decode(self, obj: JsonType) -> t.Optional[JsonType]:
        """
        In a subclass, either override this or add some decode functions and
        override __init__ to register them
        """
        pass

    def decode_numpy(self, obj: JsonType) -> t.Optional["np.ndarray"]:
        return _decode_numpy(obj)


class JSONEncoder(MethodListCaller):
    """
    Instances may be passed to simplejson as default to encode json objects.
    The encoders will be called in order. The first one to return something other
    than None wins. The encoders will be given an object to encore and should return
    a dict, something like:

        {
            "__ndarray__": [
                    [859.0, 859.0],
                    [217.0, 106.0],
                    [302.0, 140.0]
                ],
            "dtype": "float32",
            "shape": [3, 2]
        }

    Note that for default, if we want to do nothing, we return None and the object
    is encoded as best as simplejson can (which is often by throwing a TypeError).
    We override MethodListCaller.default to get this behavior.
    """

    def __init__(self, encode_as_primitives: bool = ENCODE_AS_PRIMITIVES_BY_DEFAULT):
        self.encode_as_primitives = encode_as_primitives
        self.register(self.encode_numpy)
        self.register(self.encode)

    def default(self, obj: t.Any) -> t.Optional[JsonType]:
        return None

    def encode(self, obj: t.Any) -> t.Optional[JsonType]:
        """
        In a subclass, either override this or add some encode functions and
        override __init__ to register them
        """
        pass

    def encode_numpy(self, obj: np.ndarray) -> t.Optional[JsonType]:
        return _encode_numpy(obj, as_primitives=self.encode_as_primitives)
