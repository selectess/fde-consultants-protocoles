def revenue(orders):
    return sum(amount for status, amount in orders)
