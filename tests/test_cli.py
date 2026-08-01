"""Tests for the command line interface."""

from __future__ import annotations

import json

import pytest

from quality_template.cli import main


@pytest.fixture
def sample_file(tmp_path):
    path = tmp_path / "sample.txt"
    path.write_text("The cat sat on the mat. The cat purred.", encoding="utf-8")
    return path


def test_table_output(sample_file, capsys):
    assert main([str(sample_file)]) == 0
    out = capsys.readouterr().out
    assert "words" in out
    assert "most frequent words" in out
    assert "cat" in out


def test_json_output_is_valid(sample_file, capsys):
    assert main([str(sample_file), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["words"] == 9
    assert payload["top_words"][0]["word"] == "cat"


def test_top_limit(sample_file, capsys):
    main([str(sample_file), "--json", "-n", "1"])
    assert len(json.loads(capsys.readouterr().out)["top_words"]) == 1


def test_keep_stop_words_changes_result(sample_file, capsys):
    main([str(sample_file), "--json", "--keep-stop-words", "-n", "1"])
    assert json.loads(capsys.readouterr().out)["top_words"][0]["word"] == "the"


def test_reads_stdin_when_no_path(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", __import__("io").StringIO("alpha beta alpha"))
    main(["--json"])
    assert json.loads(capsys.readouterr().out)["words"] == 3


def test_missing_file_exits_with_message(tmp_path):
    with pytest.raises(SystemExit) as exc:
        main([str(tmp_path / "nope.txt")])
    assert "no such file" in str(exc.value)


def test_version_flag(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert "quality-template" in capsys.readouterr().out


def test_empty_file(tmp_path, capsys):
    empty = tmp_path / "empty.txt"
    empty.write_text("", encoding="utf-8")
    main([str(empty), "--json"])
    payload = json.loads(capsys.readouterr().out)
    assert payload["words"] == 0
    assert payload["top_words"] == []
