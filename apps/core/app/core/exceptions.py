from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
    ) -> None:
        self.message = message
        super().__init__(status_code=status_code, detail=message)

    def to_response(self) -> dict[str, int | str]:
        return {"message": self.message, "status_code": self.status_code}


class LLMException(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, status_code=status.HTTP_502_BAD_GATEWAY)


class ConfigurationException(AppException):
    def __init__(self, message: str) -> None:
        super().__init__(message=message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
