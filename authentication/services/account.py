from typing import Annotated, Optional
from uuid import UUID

import bcrypt
from fastapi import Depends

from ..core.base import AppObject
from ..core.database import Repository
from ..core.database.repository import get_repository
from ..models import Account, User


class AccountService(AppObject):
    """
    Service for managing user accounts.

    Similar to better-auth's account management:
    - Handles password hashing and verification
    - Manages account creation and linking
    - Supports multiple providers (credential, oauth, etc.)
    """

    def __init__(
        self,
        account_repository: Annotated[
            Repository[Account], Depends(get_repository(Account))
        ],
        user_repository: Annotated[Repository[User], Depends(get_repository(User))],
    ):
        self.account_repository = account_repository
        self.user_repository = user_repository

    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        """

        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        """
        return bcrypt.checkpw(
            plain_password.encode("utf-8"), hashed_password.encode("utf-8")
        )

    async def create_credential_account(
        self,
        user_id: UUID,
        email: str,
        password: str,
    ) -> Account:
        """
        Create a credential-based account (email/password).
        Similar to better-auth's credential account creation.

        Args:
            user_id: The user ID to link the account to
            email: The email address (used as account_id)
            password: The plain text password (will be hashed)

        Returns:
            The created Account instance
        """
        hashed_password = self.hash_password(password)

        account = Account(
            user_id=user_id,
            account_id=email,
            provider_id="credential",
            password=hashed_password,
        )

        return await self.account_repository.create(account)

    async def get_account_by_email(self, email: str) -> Optional[Account]:
        """
        Get an account by email (account_id) for credential provider.
        """
        accounts = await self.account_repository.all(
            account_id=email, provider_id="credential", limit=1
        )

        if not accounts:
            return None

        return accounts[0]

    async def get_account_by_provider(
        self, account_id: str, provider_id: str
    ) -> Optional[Account]:
        """
        Get an account by provider and account_id.
        """
        accounts = await self.account_repository.all(
            account_id=account_id, provider_id=provider_id, limit=1
        )

        if not accounts:
            return None

        return accounts[0]

    async def get_user_accounts(self, user_id: UUID) -> list[Account]:
        """
        Get all accounts linked to a user.
        """
        return await self.account_repository.all(user_id=user_id)

    async def verify_credential(self, email: str, password: str) -> Optional[Account]:
        """
        Verify email and password credentials.
        Returns the account if valid, None otherwise.
        """
        account = await self.get_account_by_email(email)

        if not account or not account.password:
            return None

        if self.verify_password(password, account.password):
            return account

        return None

    async def update_account_password(
        self, account_id: UUID, new_password: str
    ) -> Account:
        """
        Update the password for an account.
        """
        hashed_password = self.hash_password(new_password)

        return await self.account_repository.update(
            account_id, password=hashed_password
        )

    async def link_account(
        self,
        user_id: UUID,
        account_id: str,
        provider_id: str,
        access_token: Optional[str] = None,
        refresh_token: Optional[str] = None,
        scope: Optional[str] = None,
        id_token: Optional[str] = None,
    ) -> Account:
        """
        Link an OAuth account to a user.
        Similar to better-auth's account linking.
        """
        account = Account(
            user_id=user_id,
            account_id=account_id,
            provider_id=provider_id,
            access_token=access_token,
            refresh_token=refresh_token,
            scope=scope,
            id_token=id_token,
        )

        return await self.account_repository.create(account)

    async def unlink_account(self, account_id: UUID) -> None:
        """
        Unlink an account from a user.
        """
        await self.account_repository.delete(account_id)
