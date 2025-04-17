class BarteError(Exception):
    """Exception raised for errors in the Barte API."""

    def __init__(
        self, message, action=None, code=None, charge_uuid=None, response=None
    ):
        self.message = message
        self.action = action
        self.code = code
        self.charge_uuid = charge_uuid
        self.response = response
        super().__init__(self.message)

    def __str__(self):
        error_msg = f"Error {self.code}: {self.message}"
        if self.action:
            error_msg += f" - Action: {self.action}"
        if self.charge_uuid:
            error_msg += f" - Charge UUID: {self.charge_uuid}"
        return error_msg
