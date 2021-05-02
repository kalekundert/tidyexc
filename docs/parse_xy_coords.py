from tidyexc import Error

class ParseError(Error):
    pass

def parse_xy_coords(path):
    with ParseError.add_info("path: {path}", path=path):
        lines = _lines_from_file(path)
        coords = []

        for i, line in enumerate(lines, 1):
            with ParseError.add_info("line #{i}: {line}", i=i, line=line):
                coord = _coord_from_line(line)
                coords.append(coord)

        return coords

def _lines_from_file(path):
    try:
        with open(path) as f:
            return f.readlines()

    except FileNotFoundError:
        err = ParseError("can't read file")
        err.hints += "Double-check that the given path actually exists."
        raise err from None

def _coord_from_line(line):
    fields = line.split()

    if len(fields) != 2:
        raise ParseError(
                lambda e: f"expected 2 fields, found {len(e.fields)}",
                fields=fields,
        )

    coord = []

    for field in fields:
        try:
            coord.append(float(field))

        except ValueError:
            raise ParseError("expected a number, not {field!r}", field=field) from None

    return tuple(coord)

##################################### >8 #####################################

import pytest
from pathlib import Path

def test_parse_xy_coords(tmp_path):
    p = tmp_path / 'input.xy'
    p.write_text("1 2\n3 4")
    assert parse_xy_coords(p) == [(1, 2), (3, 4)]

def test_parse_xy_coords_err_1(tmp_path):
    p = tmp_path / 'input.xy'

    with pytest.raises(ParseError) as err:
        parse_xy_coords(p)

    assert err.match(r"path: .*input\.xy")
    assert err.match(r"can't read file")

def test_parse_xy_coords_err_2(tmp_path):
    p = tmp_path / 'input.xy'
    p.write_text("1")

    with pytest.raises(ParseError) as err:
        parse_xy_coords(p)

    assert err.match(r"path: .*input\.xy")
    assert err.match(r"line #1: 1")
    assert err.match(r"expected 2 fields, found 1")

def test_parse_xy_coords_err_3(tmp_path):
    p = tmp_path / 'input.xy'
    p.write_text("1 b")

    with pytest.raises(ParseError) as err:
        parse_xy_coords(p)

    assert err.match(r"path: .*input\.xy")
    assert err.match(r"line #1: 1")
    assert err.match(r"expected a number, not 'b'")
