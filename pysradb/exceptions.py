"""This file contains custom Exceptions for pysradb
"""


class MissingQueryException(Exception):
    """Exception raised when the user did not supply any query fields.

    Attributes:
        message: string
            Error message for this Exception

    """

    def __init__(self):
        self.message = (
            "No valid query has been supplied. \n"
            "A query must be supplied to one of the following fields:\n"
            "[--query, --accession, --organism, --layout, --mbases, --publication-date,"
            " --platform, --selection, --source, --strategy, --title]"
        )
        super().__init__(self.message)


class IncorrectFieldException(Exception):
    """Exception raised when the user enters incorrect inputs for a flag."""

    pass
