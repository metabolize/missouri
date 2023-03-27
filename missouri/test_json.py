# Adapted from
# https://github.com/metabolize-forks/baiji-serialization/tree/8b77f19685555e1bab03e75a433d00ce6fa4bea5
# Apache 2.0

from missouri import json


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
