import csv
from collections.abc import Generator, Iterable
from io import StringIO
from typing import Protocol
from backend.exceptions import ImportValidationError


class TabularReader(Protocol):
    def read_rows(self, raw_content: str) -> Iterable[list[str]]:
        """Yield parsed rows, including blank rows as []."""
        ...


class CsvReader:
    def read_rows(self, raw_content: str) -> Generator[list[str], None, None]:
        try:
            yield from csv.reader(StringIO(raw_content))
        except csv.Error as exc:
            raise ImportValidationError(f"Malformed CSV: {exc}") from exc
