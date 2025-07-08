from pigeonium.struct import Transaction, Currency
from pigeonium.error import CanselTransaction
from typing import Literal, Optional

transaction: Transaction = Transaction()
selfAddress: bytes = bytes(16)
baseCurrency: Currency = Currency()

CanselTransaction = CanselTransaction

def hex2bytes(hex:str, length:int=None) -> bytes:
    pass

def sha256(string:bytes) -> bytes:
    pass

def sha3_256(string:bytes) -> bytes:
    pass

def sha3_512(string:bytes) -> bytes:
    pass

def getBalance(address:bytes, currencyId:bytes) -> int:
    pass

def getCurrency(currencyId:bytes) -> Currency|None:
    pass

def getSelfCurrency() -> Currency|None:
    pass

def getTransaction(indexId:int) -> Transaction|None:
    pass

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
    pass

def getVariable(address:bytes, varKey:bytes) -> bytes|None:
    pass

def setVariable(varKey:bytes, varValue:bytes):
    pass

# def transferFromUser(dest:bytes, currencyId:bytes, amount:int) -> Transaction:
#     pass

# def transferFromContract(dest:bytes, currencyId:bytes, amount:int) -> Transaction:
#     pass

def transfer(dest:bytes, currencyId:bytes, amount:int) -> Transaction:
    pass

def burn(amount:int) -> Transaction:
    pass

def mint(amount:int) -> Transaction:
    pass

def createCurrency(name:str, symbol:str, supply:int) -> Transaction:
    pass

def nextIndexId() -> int:
    pass
