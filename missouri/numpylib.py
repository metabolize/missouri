import typing as t

if t.TYPE_CHECKING:  # pragma: no cover
    try:
        import numpy as np
    except ImportError:
        # This might generate type errors, but that is okay.
        pass


def encode_numpy(obj: t.Any, as_primitives: bool) -> t.Any:
    try:
        import numpy as np
    except ImportError:
        # Clearly there won't be any numpy arrays to encode...
        return None

    if isinstance(obj, np.ndarray):
        if as_primitives:
            return obj.tolist()
        else:
            return {
                "__ndarray__": obj.tolist(),
                "dtype": obj.dtype.name,
                "shape": obj.shape,
            }
    elif isinstance(obj, (np.bool8, np.bool_)):
        return bool(obj)
    elif isinstance(
        obj,
        (
            np.half,
            np.single,
            np.double,
            np.float_,
            np.longfloat,
            np.float16,
            np.float32,
            np.float64,
        ),
    ) or (hasattr(np, "float128") and isinstance(obj, np.float128)):
        return float(obj)
    elif isinstance(
        obj,
        (
            np.byte,
            np.short,
            np.intc,
            np.int_,
            np.longlong,
            np.intp,
            np.int8,
            np.int16,
            np.int32,
            np.int64,
            np.ubyte,
            np.ushort,
            np.uintc,
            np.uint,
            np.ulonglong,
            np.uintp,
            np.uint8,
            np.uint16,
            np.uint32,
            np.uint64,
        ),
    ):
        return int(obj)
    else:
        return None


def decode_numpy(dct: t.Dict) -> t.Optional["np.ndarray"]:
    if "__ndarray__" in dct:
        try:
            import numpy as np
        except ImportError:
            raise ImportError(
                "JSON file contains numpy arrays; install numpy to load it"
            )

        return np.array(
            dct["__ndarray__"],
            dtype=np.dtype(dct["dtype"]) if "dtype" in dct else np.float64,
        )
    else:
        return None
