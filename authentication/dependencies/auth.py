from enum import Enum
from typing import Annotated, Optional, Tuple

from fastapi import Depends, Cookie
from fastapi.security import OAuth2PasswordBearer

from ..core.database import Repository
from ..core.database.repository import get_repository
from ..core.exceptions import AuthenticationError
from ..models import User
from ..services import SessionService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token", auto_error=False)


class Authentication:
    class Priority(Enum):
        COOKIE_FIRST = "cookie_first"
        HEADER_FIRST = "header_first"

    class Type(Enum):
        COOKIE = "cookie"
        HEADER = "header"
        BOTH = "both"

    def __init__(
        self,
        user_repository: Annotated[Repository[User], Depends(get_repository(User))],
        session_service: Annotated[SessionService, Depends()],
        priority: Priority = Priority.COOKIE_FIRST,
        auth_type: Type = Type.BOTH,
        strict: bool = True,
    ):
        self.user_repository = user_repository
        self.session_service = session_service
        self.priority = priority
        self.type = auth_type
        self.strict = strict

    async def __call__(
        self,
        header_token: Annotated[Optional[str], Depends(oauth2_scheme)],
        cookie_token: Annotated[Optional[str], Cookie(alias="session_token")],
    ) -> Optional[User]:
        token, token_type = self.__get_token(header_token, cookie_token)

        if not token:
            if self.strict:
                raise AuthenticationError(
                    "Authentication credentials were not provided"
                )
            return None

        if token_type == self.Type.HEADER:
            payload = self.session_service.verify_jwt_token(token)

            if not payload and self.strict:
                raise AuthenticationError("Invalid or expired JWT token")

            return await self.user_repository.get_first(id=payload.sub)

        session = await self.session_service.get_session_by_token(token)

        if not session and self.strict:
            raise AuthenticationError("Invalid or expired session token")

        return session.user

    def __get_token(
        self, header_token: Optional[str], cookie_token: Optional[str]
    ) -> Tuple[Optional[str], Optional["Authentication.Type"]]:
        if self.type == self.Type.COOKIE:
            return cookie_token, self.Type.COOKIE

        if self.type == self.Type.HEADER:
            return header_token, self.Type.HEADER

        # Method.BOTH
        if self.priority == self.Priority.COOKIE_FIRST:
            return (
                (cookie_token, self.Type.COOKIE)
                if cookie_token
                else (header_token, self.Type.HEADER)
            )

        return (
            (header_token, self.Type.HEADER)
            if header_token
            else (cookie_token, self.Type.COOKIE)
        )
