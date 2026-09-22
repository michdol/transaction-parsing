import re
from dataclasses import dataclass
from datetime import date
from typing import Protocol
from backend.exceptions import ImportValidationError

REQUIRED_HEADERS = {"transaction_id", "date", "customer", "amount", "currency"}
MAX_AMOUNT_MINOR = 100_000_000
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
AMOUNT_RE = re.compile(r"^\d+(\.\d{1,2})?$")


class HeaderValidator:
    def validate(self, header: list[str]) -> None:
        if len(header) != len(set(header)):
            raise ImportValidationError("Duplicate header column names")

        if set(header) != REQUIRED_HEADERS:
            raise ImportValidationError(
                "Header must contain exactly: "
                "transaction_id, date, customer, amount, currency"
            )


@dataclass(frozen=True)
class AcceptedTransaction:
    transaction_id: str
    date: str
    customer: str
    currency: str
    amount_minor: int

    def as_dict(self) -> dict:
        return {
            "transaction_id": self.transaction_id,
            "date": self.date,
            "customer": self.customer,
            "currency": self.currency,
            "amount_minor": self.amount_minor,
        }


class TransactionValidator(Protocol):
    def validate(
        self, record: dict[str, str], seen_ids: set[str]
    ) -> str | AcceptedTransaction:
        """Return a rejection reason or an accepted transaction."""
        ...


class DefaultTransactionValidator:
    def validate(
        self, record: dict[str, str], seen_ids: set[str]
    ) -> str | AcceptedTransaction:
        transaction_id = record["transaction_id"]
        customer = record["customer"]
        date_value = record["date"]
        amount_value = record["amount"]
        currency = record["currency"]

        if not transaction_id:
            return "transaction_id is empty"
        if not customer:
            return "customer is empty"
        if not self._valid_date(date_value):
            return "date is not a valid YYYY-MM-DD calendar date"

        amount_minor = self._amount_minor(amount_value)
        if amount_minor is None:
            return "amount is not a positive decimal with up to two decimal places"
        if amount_minor <= 0:
            return "amount must be positive"
        if amount_minor > MAX_AMOUNT_MINOR:
            return "amount exceeds the maximum of 1,000,000.00"
        if currency != "EUR":
            return "currency must be EUR"
        if transaction_id in seen_ids:
            return f"duplicate transaction_id '{transaction_id}'"

        return AcceptedTransaction(
            transaction_id=transaction_id,
            date=date_value,
            customer=customer,
            currency=currency,
            amount_minor=amount_minor,
        )

    @staticmethod
    def _valid_date(value: str) -> bool:
        if not DATE_RE.fullmatch(value):
            return False

        try:
            year, month, day = map(int, value.split("-"))
            date(year, month, day)
            return True
        except ValueError:
            return False

    @staticmethod
    def _amount_minor(value: str) -> int | None:
        if not AMOUNT_RE.fullmatch(value):
            return None

        whole, _, fraction = value.partition(".")
        return int(whole) * 100 + int(fraction.ljust(2, "0"))
