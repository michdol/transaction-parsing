class ImportValidationError(Exception):
    """Raised when the CSV itself is structurally invalid.

    This is distinct from a row being rejected: a structural problem
    (missing/duplicate/malformed headers, unparsable CSV) means no import
    is created at all.
    """
