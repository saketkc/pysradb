# Contributing

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at <https://github.com/saketkc/pysradb/issues>.

If you are reporting a bug, please include:

-   Your operating system name and version.
-   Any details about your local setup that might be helpful in
    troubleshooting.
-   Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with \"bug\"
and \"help wanted\" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with
\"enhancement\" and \"help wanted\" is open to whoever wants to
implement it.

### Write Documentation

pysradb could always use more documentation, whether as part of the
official pysradb docs, in docstrings, or even on the web in blog posts,
articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at
<https://github.com/saketkc/pysradb/issues>.

If you are proposing a feature:

-   Explain in detail how it would work.
-   Keep the scope as narrow as possible, to make it easier to
    implement.
-   Remember that this is a volunteer-driven project, and that
    contributions are welcome :)

## Get Started

Ready to contribute? Here is how to set up `pysradb` for local development.

1.  Fork the [pysradb]{.title-ref} repo on GitHub.

2.  Clone your fork locally:

    ``` shell
    $ git clone git@github.com:your_name_here/pysradb.git
    ```

3.  Install your local copy in editable mode with the development extras:

    ``` shell
    $ cd pysradb/
    $ python -m pip install --upgrade pip
    $ python -m pip install --editable ".[test,docs]"
    ```

4.  Create a branch for local development:

    ``` shell
    $ git checkout -b name-of-your-bugfix-or-feature
    ```

    Now you can make your changes locally.

5.  When you are done making changes, check that lint, tests,
    packaging, and documentation pass locally:

    ``` shell
    $ flake8 pysradb tests
    $ coverage run --source pysradb -m pytest
    $ coverage report -m
    $ python -m build
    $ make docs
    ```

    The docs build includes notebooks and uses the Furo Sphinx theme.

6.  Commit your changes and push your branch to GitHub:

    ``` shell
    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature
    ```

7.  Submit a pull request through the GitHub website.

Direct pushes to protected branches are discouraged. Use a pull request
for normal changes so tests, package build, and documentation build run
before the change is merged.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1.  The pull request should include tests.
2.  If the pull request adds functionality, the docs should be updated.
    Put your new functionality into a function with a docstring, and add
    the feature to the list in README.rst.
3.  The pull request should work for the Python versions declared in
    `pyproject.toml`. GitHub Actions runs tests across the supported
    Python matrix.

## Tips

To run a subset of tests:

``` shell
$ pytest tests/test_sraweb.py
```

## Deploying

A reminder for maintainers: releases are built from `pyproject.toml`.
Make sure all changes are committed and reviewed through a pull request
before creating a GitHub release.

``` shell
$ python -m build
```

The publish workflow uploads the built artifacts to PyPI when a GitHub
release is created.
