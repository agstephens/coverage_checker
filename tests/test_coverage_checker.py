#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `coverage_checker` package."""

import pytest
import os

from click.testing import CliRunner

from coverage_checker.coverage_checker import check_coverage
from coverage_checker import cli


TOP_DIR = 'top_dir'
SYMLINK_TARGET = '/tmp/test-symlink'


def setup():
    with open(SYMLINK_TARGET, 'w') as writer:
        writer.write('hi')


def teardown():
    os.remove(SYMLINK_TARGET)


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'coverage_checker.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output


def _create_paths_and_enter_dir(tmpdir, items):

    base = tmpdir.mkdir(TOP_DIR)
    paths = []

    for item in items:
        _ = base.join(item)

        # It is a file if '.' found in name
        if _.basename == 'symlink':
            _.mksymlinkto(SYMLINK_TARGET)
        elif '.' in _.basename:
            _.write('data', ensure=True)
        else:
            _.ensure(dir=True)

        paths.append(_)

    os.chdir(base.dirname)
    return paths


def test_check_coverage_success_1(tmpdir):
    paths = ('a/b/c/d/1.dat', 'a/b/c/d/2.dat')
    _create_paths_and_enter_dir(tmpdir, paths)

    resp = check_coverage(TOP_DIR, depth=5)
    assert(resp == [0, 0, 0, ''])


def test_check_coverage_success_2_ignore_empty_dir(tmpdir):
    paths = ('a/b/c/d/1.dat', 'a/b/c/d/2.dat', 'a/b/z')
    _create_paths_and_enter_dir(tmpdir, paths)

    resp = check_coverage(TOP_DIR, depth=5, ignore_empty_dirs=True)
    assert(resp == [0, 0, 0, ''])


def test_check_coverage_success_3_ignore_symlink(tmpdir):
    paths = ('a/b/c/d/1.dat', 'a/b/c/d/2.dat', 'a/b/symlink')
    _create_paths_and_enter_dir(tmpdir, paths)

    resp = check_coverage(TOP_DIR, depth=5, ignore_symlinks=True)
    assert(resp == [0, 0, 0, ''])


def test_check_coverage_success_4_ignore_file(tmpdir):
    paths = ('a/b/c/d/1.dat', 'a/b/c/d/2.dat', 'a/b/bad.txt')
    _create_paths_and_enter_dir(tmpdir, paths)

    resp = check_coverage(TOP_DIR, depth=5, ignore_files=True)
    assert(resp == [0, 0, 0, ''])


def test_check_coverage_success_5_ignore_patterns(tmpdir):
    paths = ('a/b/c/d/1.dat', 'a/b/c/d/2.dat', 'a/b/bad.txt', 'random')
    _create_paths_and_enter_dir(tmpdir, paths)

    resp = check_coverage(TOP_DIR, depth=5, ignores=('bad.*', 'ran.om'))
    assert(resp == [0, 0, 0, ''])


def test_check_coverage_fail_1_wrong_depth(tmpdir):
    paths = ('a/b/c/d/1.dat', 'a/b/c/d/2.dat')
    _create_paths_and_enter_dir(tmpdir, paths)

    resp = check_coverage(TOP_DIR, depth=4)
    assert(resp[0] == 1), resp


def test_check_coverage_fail_2_different_depths(tmpdir):
    paths = ('a/b/c/d/1.dat', 'a/b/c/d/2.dat', 'a/b/3.dat')
    _create_paths_and_enter_dir(tmpdir, paths)

    resp = check_coverage(TOP_DIR, depth=4)
    assert(resp[0] == 1), resp


def test_check_coverage_fail_3_empty_dir(tmpdir):
    paths = ('a/b/c/d/1.dat', 'a/b/c/d/2.dat', 'a/b/z')
    _create_paths_and_enter_dir(tmpdir, paths)

    resp = check_coverage(TOP_DIR, depth=5)
    assert(resp[2] == 1), resp


def test_check_coverage_fail_4_ignore_patterns(tmpdir):
    paths = ('a/b/c/d/1.dat', 'a/b/c/d/2.dat', 'a/b/bad.txt', 'random')
    _create_paths_and_enter_dir(tmpdir, paths)

    resp = check_coverage(TOP_DIR, depth=5, ignores=('bad.*', 'ran.kom'))
    assert(resp[:3] == [0, 0, 1]), resp
