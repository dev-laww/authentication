from ..core.base import Controller
from ..core.exceptions import NoImplementationError
from ..schemas.auth import EmailLogin


class AuthController(Controller):
    async def login(self, login: EmailLogin):
        raise NoImplementationError("Login not implemented yet")

    async def logout(self):
        raise NoImplementationError("Logout not implemented yet")

    async def refresh_token(self):
        raise NoImplementationError("Refresh token not implemented yet")

    async def register(self):
        raise NoImplementationError("Registration not implemented yet")

    async def verify_email(self):
        raise NoImplementationError("Email verification not implemented yet")

    async def send_verification_email(self):
        raise NoImplementationError("Resend verification email not implemented yet")

    async def social_login(self):
        raise NoImplementationError("Social login not implemented yet")

    async def forgot_password(self):
        raise NoImplementationError("Password reset not implemented yet")

    async def reset_password(self):
        raise NoImplementationError("Change password not implemented yet")
