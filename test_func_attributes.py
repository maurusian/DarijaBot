def fact(x):
    fact.count = 0
    def _fact(x,c):
        c+=1
        fact.count+=1
        if fact.count >10:
            return 0
        if x == 0:
            return 1
        else:
            return _fact(x-1,c)*x
    return _fact(x,fact.count)


print(fact(15))
print(fact.count)
