from pigeonium.struct import Transaction, Currency
from pigeonium.error import CanselTransaction
from typing import Literal, Optional

transaction: Transaction = Transaction()
selfAddress: bytes = bytes(16)
baseCurrency: Currency = Currency()

CanselTransaction = CanselTransaction

def hex2bytes(hex:str, length:int=None) -> bytes:
    ...

def sha256(string:bytes) -> bytes:
    ...

def sha3_256(string:bytes) -> bytes:
    ...

def sha3_512(string:bytes) -> bytes:
    ...

def getBalance(address:bytes, currencyId:bytes) -> int:
    ...

def getCurrency(
        currencyId:Optional[bytes]=None,
        name:Optional[str]=None,
        symbol:Optional[str]=None,
        issuer:Optional[bytes]=None
    ) -> Currency|None:
    ...

def getSelfCurrency() -> Currency|None:
    ...

def getTransaction(indexId:int) -> Transaction|None:
    ...

def getTransactions(
        self,
        address: Optional[bytes] = None,
        source: Optional[bytes] = None,
        dest: Optional[bytes] = None,
        currencyId: Optional[bytes] = None,
        amount_min: Optional[int] = None,
        amount_max: Optional[int] = None,
        timestamp_start: Optional[int] = None,
        timestamp_end: Optional[int] = None,
        isContract: Optional[bool] = None,
        sort_by: Literal["indexId", "timestamp", "amount", "feeAmount"] = "indexId",
        sort_order: Literal["ASC", "DESC"] = "DESC",
        limit: int = 20,
        offset: int = 0
    ) -> list[Transaction]:
    ...

def getVariable(address:bytes, varKey:bytes) -> bytes|None:
    ...

def setVariable(varKey:bytes, varValue:bytes|None):
    if varValue is None:
        delVariable(varKey)
    else:
        ...

def delVariable(varKey:bytes):
    ...

# def transferFromUser(dest:bytes, currencyId:bytes, amount:int) -> Transaction:
#     ...

# def transferFromContract(dest:bytes, currencyId:bytes, amount:int) -> Transaction:
#     ...

def transfer(dest:bytes, currencyId:bytes, amount:int) -> Transaction:
    ...

def burn(amount:int) -> Transaction:
    ...

def mint(amount:int) -> Transaction:
    ...

def createCurrency(name:str, symbol:str, supply:int) -> Transaction:
    ...

def nextIndexId() -> int:
    ...
