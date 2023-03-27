# Adapted from
# https://github.com/metabolize-forks/baiji-serialization/tree/8b77f19685555e1bab03e75a433d00ce6fa4bea5
# Apache 2.0

from missouri import json
import pytest


def test_json_dumps() -> None:
    """Examples from json docs"""
    assert (
        json.dumps(["foo", {"bar": ("baz", None, 1.0, 2)}])
        == r'["foo", {"bar": ["baz", null, 1.0, 2]}]'
    )
    assert json.dumps('"foo\bar') == r'"\"foo\bar"'
    assert json.dumps("\u1234") == r'"\u1234"'
    assert json.dumps("\\") == r'"\\"'
    assert (
        json.dumps({"c": 0, "b": 0, "a": 0}, sort_keys=True)
        == r'{"a": 0, "b": 0, "c": 0}'
    )
    assert (
        json.dumps([1, 2, 3, {"4": 5, "6": 7}], separators=(",", ":"))
        == r'[1,2,3,{"4":5,"6":7}]'
    )
    assert (
        json.dumps({"4": 5, "6": 7}, sort_keys=True, indent=4, separators=(",", ": "))
        == '{\n    "4": 5,\n    "6": 7\n}'
    )


def test_json_dump_stringio() -> None:
    from io import StringIO

    io = StringIO()
    json.dump(["streaming API"], io)
    assert io.getvalue() == r'["streaming API"]'


def test_json_dump_file(tmpdir) -> None:
    path = str(tmpdir / "test_json_dump_file.json")
    with open(path, "w") as f:
        json.dump(["File Test"], f)
    with open(path, "r") as f:
        assert f.read() == r'["File Test"]'


def test_json_dump_path(tmpdir) -> None:
    path = str(tmpdir / "test_json_dump_path.json")
    json.dump(["File Test"], path)
    with open(path, "r") as f:
        assert f.read() == r'["File Test"]'


def test_json_loads() -> None:
    assert json.loads('["foo", {"bar":["baz", null, 1.0, 2]}]') == [
        "foo",
        {"bar": ["baz", None, 1.0, 2]},
    ]
    assert json.loads('"\\"foo\\bar"') == '"foo\x08ar'


def test_json_load_stringio() -> None:
    from io import StringIO

    io = StringIO('["streaming API"]')
    assert json.load(io) == ["streaming API"]


def test_json_load_file(tmpdir) -> None:
    path = str(tmpdir / "test_json_load_file.json")
    with open(path, "w") as f:
        f.write(r'["File Test"]')
    with open(path, "r") as f:
        assert json.load(f) == ["File Test"]


def test_json_load_path(tmpdir) -> None:
    path = str(tmpdir / "test_json_load_path.json")
    with open(path, "w") as f:
        f.write(r'["File Test"]')
    assert json.load(path) == ["File Test"]


def test_json_load_ndarray_tricks_compatible_1d() -> None:
    import numpy as np

    res = json.loads(
        '{"foo": {"__ndarray__": [859.033935546875, 859.033935546875], "dtype": "float32", "shape": [2]}}'
    )
    res_array = res["foo"]
    assert isinstance(res_array, np.ndarray)
    assert res_array.shape == (2,)
    assert res_array.dtype == np.float32
    np.testing.assert_equal(res_array, np.array([859.033935546875, 859.033935546875]))


def test_json_load_ndarray_tricks_compatible_2d() -> None:
    import numpy as np

    res = json.loads(
        '{"foo": {"__ndarray__": [[859.0, 859.0], [217.0, 106.0], [302.0, 140.0]], "dtype": "float32", "shape": [3, 2]}}'  # noqa: E501
    )
    res_array = res["foo"]
    assert isinstance(res_array, np.ndarray)
    assert res_array.shape == (3, 2)
    assert res_array.dtype == np.float32
    np.testing.assert_almost_equal(
        res_array, np.array([[859.0, 859.0], [217.0, 106.0], [302.0, 140.0]])
    )


def test_json_dump_ndarray_tricks_compatible() -> None:
    import numpy as np

    assert (
        json.dumps(
            {
                "foo": np.array(
                    [[859.0, 859.0], [217.0, 106.0], [302.0, 140.0]],
                    dtype=np.float32,
                )
            },
        )
        == r'{"foo": {"__ndarray__": [[859.0, 859.0], [217.0, 106.0], [302.0, 140.0]], "dtype": "float32", "shape": [3, 2]}}'  # noqa: E501
    )


def test_json_dump_ndarray_tricks_as_primitives() -> None:
    import numpy as np

    assert (
        json.dumps(
            {
                "foo": np.array(
                    [[859.0, 859.0], [217.0, 106.0], [302.0, 140.0]],
                    dtype=np.float32,
                )
            },
            encode_as_primitives=True,
        )
        == r'{"foo": [[859.0, 859.0], [217.0, 106.0], [302.0, 140.0]]}'
    )


def test_json_dump_np_scalars() -> None:
    import numpy as np

    assert json.dumps(np.bool_(True)) == "true"
    assert json.dumps(np.float128(3.14)) == "3.14"
    assert json.dumps(np.short(3)) == "3"


def test_json_dump_custom_encoder():
    from missouri.coding import JSONEncoder

    class MyClass:
        pass

    class MyEncoder(JSONEncoder):
        def encode(self, obj):
            if isinstance(obj, MyClass):
                return {"oh yes": "it's my class"}
            else:
                return None

    assert (
        json.dumps(MyClass(), encoder=MyEncoder()) == """{"oh yes": "it's my class"}"""
    )


def test_json_dump_dict_kwarg_raises_expected_error(tmpdir):
    with pytest.raises(
        ValueError,
        match=r"Instead of explicitly setting default, subclass missouri.coding.JSONEncoder and pass it as encoder",
    ):
        json.dump({"foo": 123}, str(tmpdir / "test_example.json"), default=dict())


def test_json_load_custom_decoder():
    from missouri.coding import JSONDecoder

    class MyClass:
        pass

    class MyDecoder(JSONDecoder):
        def decode(self, obj):
            if list(obj.keys()) == ["oh yes"]:
                return MyClass()
            else:
                return None

    assert isinstance(
        json.loads("""{"oh yes": "it's my class"}""", decoder=MyDecoder()), MyClass
    )


def test_json_load_object_hook_kwarg_raises_expected_error():
    with pytest.raises(
        ValueError,
        match=r"Instead of explicitly setting object_hook, subclass missouri.coding.JSONDecoder and pass it as decoder",
    ):
        json.load("test_example.json", object_hook=dict())


def test_json_dump_unknown_object_raises_expected():
    class MyClass:
        pass

    with pytest.raises(
        ValueError,
        match=r"Object of type <class .* is not JSON-serializable",
    ):
        json.dumps(MyClass())


def test_json_dump_does_not_raise_importerror_when_numpy_is_not_installed(monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, "numpy", None)

    with pytest.raises(
        ValueError, match=r"Object of type <class 'complex'> is not JSON-serializable"
    ):
        json.dumps(complex(1, 3))


def test_json_load_raises_expected_error_when_numpy_is_not_installed(monkeypatch):
    import sys

    monkeypatch.setitem(sys.modules, "numpy", None)

    with pytest.raises(
        ImportError, match=r"JSON file contains numpy arrays; install numpy to load it"
    ):
        json.loads(
            r'{"foo": {"__ndarray__": [[859.0, 859.0], [217.0, 106.0], [302.0, 140.0]], "dtype": "float32", "shape": [3, 2]}}'
        )


def test_json_dump_raises_expected_error_with_non_file_object():
    with pytest.raises(
        ValueError, match=r"Object does not appear to be a path or a file-like object"
    ):
        json.dump({"some": "data"}, dict())
