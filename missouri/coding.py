# Adapted from
# https://github.com/metabolize-forks/baiji-serialization/tree/8b77f19685555e1bab03e75a433d00ce6fa4bea5
# Apache 2.0

import typing as t
from .numpylib import decode_numpy as _decode_numpy, encode_numpy as _encode_numpy

if t.TYPE_CHECKING:  # pragma: no cover
    import numpy as np

# TODO: Refine this type.
CoderMethod = t.Callable[[t.Any], t.Any]


class MethodListCaller:
    """
    This is an internal class that lets the JSON(En,De)coder classes
    and their subclasses easily register a list of methods to try, which
    will then be called in order until one of them succeeds.
    """

    method_list: t.List[CoderMethod]

    def register(self, method: CoderMethod, index: int = -1) -> None:
        if not hasattr(self, "method_list"):
            self.clear()
        if index == -1:
            index = len(self.method_list)
        self.method_list.insert(index, method)

    def clear(self) -> None:
        # be defensive if someone forgets to call super pylint: disable=attribute-defined-outside-init
        self.method_list = []

    def __call__(self, obj: t.Any) -> t.Any:
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

    def default(self, x: t.Any) -> t.Any:
        """
        If none of the methods returned something, then return this default
        """
        return x


class JSONEncoder(MethodListCaller):
    """
    Instances may be passed to simplejson as default to encode json objects.
    The encoders will be called in order. The first one to return something other
    than None wins. The encoders will be given an object to encore and should return
    a dict, something like:

    .. code-block:: python

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

    def __init__(self, encode_as_primitives: t.Optional[bool] = None):
        self.encode_as_primitives = (
            False if encode_as_primitives is None else encode_as_primitives
        )
        self.register(self.encode)
        self.register(self.encode_numpy)

    def default(self, obj: t.Any) -> t.Any:
        raise ValueError(f"Object of type {type(obj)} is not JSON-serializable")

    def encode(self, obj: t.Any) -> t.Any:
        """
        In a subclass, either override this or add some encode functions and
        override __init__ to register them.
        """
        pass

    def encode_numpy(self, obj: "np.ndarray") -> t.Any:
        return _encode_numpy(obj, as_primitives=self.encode_as_primitives)


class JSONDecoder(MethodListCaller):
    """
    Instances may be passed to simplejson as object_hook to decode json objects.
    The decoders will be called in order. The first one to return something other
    than None wins. The decoders will be given a dict to parse, something like:

    .. code-block:: python

        {
            "__ndarray__": [
                [859.0, 859.0],
                [217.0, 106.0],
                [302.0, 140.0]
            ],
            "dtype": "float32",
            "shape": [3, 2]
        }

    Note that for `object_hook`, if we want to do nothing, we return the dict unchanged
    and the json is decoded as a plain old dict; this behavior is the default of
    MethodListCaller.
    """

    def __init__(self) -> None:
        self.register(self.decode)
        self.register(self.decode_numpy)

    def decode(self, obj: t.Any) -> t.Any:
        """
        In a subclass, either override this or add some decode functions and
        override __init__ to register them
        """
        pass

    def decode_numpy(self, obj: t.Any) -> t.Optional["np.ndarray"]:
        return _decode_numpy(obj)
