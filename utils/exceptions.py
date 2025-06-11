class APIError(Exception):
    def __init__(self, status: int, payload: dict | str):
        self.status = status
        self.payload = payload
        super().__init__(f"APIError: status={status}, payload={payload!r}")
