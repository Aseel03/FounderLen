from founderlens.engine.accounts import (
    ACCOUNT_METADATA,
    Account,
    AccountType,
    Side,
)


def test_every_account_has_metadata():
    assert set(Account) == set(ACCOUNT_METADATA.keys())


def test_account_codes_are_unique():
    declared_members = Account.__members__.values()
    distinct_codes = {account.value for account in declared_members}

    assert len(Account.__members__) == len(distinct_codes)


def test_normal_sides_are_correct():
    expected_sides = {
        AccountType.ASSET: Side.DEBIT,
        AccountType.EXPENSE: Side.DEBIT,
        AccountType.LIABILITY: Side.CREDIT,
        AccountType.EQUITY: Side.CREDIT,
        AccountType.INCOME: Side.CREDIT,
    }

    for account, metadata in ACCOUNT_METADATA.items():
        assert metadata.normal_side == expected_sides[metadata.account_type]