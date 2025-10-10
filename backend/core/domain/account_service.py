from sqlalchemy.ext.asyncio import AsyncSession

from core.converters import orm_list_to_pydantic, orm_to_pydantic
from core.domain.schemas import AccountDetails
from core.repository import AsyncAccountRepositoryWithID


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
