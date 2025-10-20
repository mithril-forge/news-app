from sqlalchemy.ext.asyncio import AsyncSession

from core.converters import orm_list_to_pydantic, orm_to_pydantic
from core.domain.schemas import AccountDetails
from core.repository import AsyncAccountRepositoryWithID, TokenGenerationResponse


class AccountService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.account_repo = AsyncAccountRepositoryWithID(session=session)

    async def set_prompt(self, account_email: str, prompt: str) -> None:
        """Set the prompt for the user."""
        account = await self.account_repo.update_prompt(email=account_email, prompt=prompt)
        if account is None:
            # Account doesn't exist, create it
            await self.account_repo.add({"email": account_email, "prompt": prompt})

    async def get_account_details(self, account_email: str) -> AccountDetails | None:
        """Get the account details for the user."""
        account_model = await self.account_repo.get_by_email(email=account_email)
        if account_model is None:
            return None
        return orm_to_pydantic(account_model, AccountDetails)

    async def get_accounts(self) -> list[AccountDetails]:
        """Get all accounts"""
        accounts = await self.account_repo.get_all()
        return orm_list_to_pydantic(accounts, AccountDetails)

    async def delete_account(self, account_email: str) -> None:
        """Deletes the account"""
        await self.account_repo.delete_by_email(account_email=account_email)

    async def create_deletion_token(
        self,
        email: str,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> TokenGenerationResponse:
        """
        Create a deletion token for an account.

        Args:
            email: Email of the account to delete
            ip_address: IP address of the requester
            user_agent: User agent string of the requester

        Returns:
            Tuple of (plain_token, token_record)

        Raises:
            AccountNotFoundException: If account with email doesn't exist
        """
        return await self.account_repo.create_deletion_token(
            email=email,
            ip_address=ip_address,
            user_agent=user_agent,
        )

    async def verify_and_delete_account(self, plain_token: str) -> None:
        """
        Verify deletion token and delete account if valid.

        Args:
            plain_token: The plain text token from the email link

        Raises:
            TokenNotFoundException: If token doesn't exist
            TokenAlreadyUsedException: If token was already used
            TokenExpiredException: If token has expired
            AccountNotFoundException: If account doesn't exist
            AccountDeletionFailedException: If deletion fails
        """
        await self.account_repo.verify_and_delete_account(plain_token=plain_token)
