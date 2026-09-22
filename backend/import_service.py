from collections.abc import Iterable

from backend.readers import CsvReader, TabularReader
from backend.validators import (
    AcceptedTransaction,
    DefaultTransactionValidator,
    HeaderValidator,
    ImportValidationError,
    TransactionValidator,
)


class ImportService:
    def __init__(
        self,
        reader: TabularReader | None = None,
        header_validator: HeaderValidator | None = None,
        transaction_validator: TransactionValidator | None = None,
    ) -> None:
        self.reader = reader or CsvReader()
        self.header_validator = header_validator or HeaderValidator()
        self.transaction_validator = (
            transaction_validator or DefaultTransactionValidator()
        )

    def evaluate(self, content: str) -> dict:
        rows = iter(self.reader.read_rows(content))
        header, header_row_number = self._find_header(rows)

        self.header_validator.validate(header)

        accepted: list[dict] = []
        rejected: list[dict] = []
        seen_ids: set[str] = set()
        total_minor = 0

        for row_number, raw_row in enumerate(rows, start=header_row_number + 1):
            if not raw_row:
                continue

            if len(raw_row) != len(header):
                rejected.append(
                    {
                        "row": row_number,
                        "reason": f"expected {len(header)} fields, found {len(raw_row)}",
                    }
                )
                continue

            record = {
                field: value.strip()
                for field, value in zip(header, raw_row, strict=True)
            }

            result = self.transaction_validator.validate(record, seen_ids)
            if isinstance(result, str):
                rejected.append({"row": row_number, "reason": result})
                continue

            seen_ids.add(result.transaction_id)
            accepted.append(result.as_dict())
            total_minor += result.amount_minor

        return {
            "accepted": accepted,
            "rejected": rejected,
            "accepted_count": len(accepted),
            "rejected_count": len(rejected),
            "total_minor": total_minor,
            "currency": "EUR",
        }

    @staticmethod
    def _find_header(
        rows: Iterable[list[str]],
    ) -> tuple[list[str], int]:
        for row_number, row in enumerate(rows, start=1):
            if row:
                return row, row_number

        raise ImportValidationError("CSV is empty; a header row is required")
