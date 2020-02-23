from conduit.apps.core.utils import generate_random_string, DEFAULT_CHAR_STRING


def test_generate_random_string():
    ret = generate_random_string(size=8)

    assert len(ret) == 8

    for c in ret:
        assert c in DEFAULT_CHAR_STRING
