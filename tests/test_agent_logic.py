from agent import _parse_exit_code


def test_parses_explicit_exit_code():
    assert _parse_exit_code("Process exited with code 1\nSTDERR: oops") == 1
    assert _parse_exit_code("Process exited with code 137") == 137


def test_treats_error_prefix_as_failure():
    assert _parse_exit_code("Error: file not found") == 1


def test_treats_clean_output_as_success():
    assert _parse_exit_code("STDOUT:\nhello world\n") == 0
