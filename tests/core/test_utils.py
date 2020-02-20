from conduit.apps.core.utils import generate_random_string


def test_generate_random_string():
    ret = generate_random_string()
    assert len(ret) == 6
