from dataclasses import dataclass
from enum import StrEnum


class AccountType(StrEnum):
    ASSET = "ASSET"
    LIABILITY = "LIABILITY"
    EQUITY = "EQUITY"
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"


class Side(StrEnum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class Account(StrEnum):
    CASH = "1000"
    EQUITY = "3000"
    REVENUE = "4000"
    MARKETING = "5000"
    PAYROLL = "6000"
    OTHER_EXPENSE = "6100"


@dataclass(frozen=True)
class AccountMetadata:
    name: str
    account_type: AccountType

    @property
    def normal_side(self) -> Side:
        return NORMAL_SIDE_BY_TYPE[self.account_type]


NORMAL_SIDE_BY_TYPE: dict[AccountType, Side] = {
    AccountType.ASSET: Side.DEBIT,
    AccountType.EXPENSE: Side.DEBIT,
    AccountType.LIABILITY: Side.CREDIT,
    AccountType.EQUITY: Side.CREDIT,
    AccountType.INCOME: Side.CREDIT,
}


ACCOUNT_METADATA: dict[Account, AccountMetadata] = {
    Account.CASH: AccountMetadata(
        name="Cash",
        account_type=AccountType.ASSET,
    ),
    Account.EQUITY: AccountMetadata(
        name="Equity",
        account_type=AccountType.EQUITY,
    ),
    Account.REVENUE: AccountMetadata(
        name="Revenue",
        account_type=AccountType.INCOME,
    ),
    Account.MARKETING: AccountMetadata(
        name="Marketing",
        account_type=AccountType.EXPENSE,
    ),
    Account.PAYROLL: AccountMetadata(
        name="Payroll",
        account_type=AccountType.EXPENSE,
    ),
    Account.OTHER_EXPENSE: AccountMetadata(
        name="Other Expense",
        account_type=AccountType.EXPENSE,
    ),
}