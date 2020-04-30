import os

from ethel.api import utils


def test_template_reads_correct_file(mocker):
    """Should read file at relative path."""
    read = mocker.mock_open(read_data="abc")
    template_file = mocker.patch("builtins.open", read)
    utils.Template("template_file.yml")
    path = os.path.join(os.path.dirname(utils.__file__), "template_file.yml")

    template_file.assert_called_once_with(path, "r")


def test_template_renders(mocker):
    """Should render YAML properly."""
    read = mocker.mock_open(read_data="key: {{ key }}")
    mocker.patch("builtins.open", read)
    template = utils.Template("template_file.yml")

    assert template.render(key="value") == {"key": "value"}
