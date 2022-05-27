from flexlate.temp_path import create_temp_path


def test_temp_path_resolves_to_be_the_same_path():
    # Note that this would work with tempfile.TemporaryDirectory on Linux and Windows, but not MacOS
    # that uses symlinks in temp paths
    with create_temp_path() as path:
        assert path == path.resolve()
