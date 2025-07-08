from funcHint import *
# Currency deposit system

selfCurrencyId = getSelfCurrency().currencyId if getSelfCurrency() else None

if not selfCurrencyId:
    createCurrency("DepoToken","DPT",1_000_000_000_000000)
    transfer(transaction.source,getSelfCurrency().currencyId,50_000_000_000000)
    selfCurrencyId = getSelfCurrency().currencyId
else:
    depo_amount = getVariable(selfAddress,transaction.source)
    depo_time = getVariable(selfAddress,sha256(transaction.source)[:16])
    if depo_amount and depo_time:
        depoTime = int.from_bytes(depo_time,'big')
        depoAmount = int.from_bytes(depo_amount,'big')
        depoPeriod = transaction.timestamp - depoTime
        if depoPeriod < 60*60: transfer(transaction.source,selfCurrencyId,depoAmount)
        else:
            interestRate = 1 + depoPeriod/(60*60) * 0.001
            return_amount = int(depoAmount*(interestRate))
            bal = getBalance(selfAddress,selfCurrencyId)
            transfer(transaction.source,selfCurrencyId,return_amount if return_amount <= bal else bal)

if transaction.currencyId == selfCurrencyId:
    setVariable(transaction.source,transaction.amount.to_bytes(8,'big'))
    setVariable(sha256(transaction.source)[:16],transaction.timestamp.to_bytes(8,'big'))
else: # Unsupported currencies
    transfer(transaction.source,transaction.currencyId,transaction.amount)
