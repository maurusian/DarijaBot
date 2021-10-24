CRYPTOS = "./data/cryptos.json"


with open(CRYPTOS,'r') as f:
    crypto_dict = eval(f.read())


print(type(crypto_dict))
print(type(crypto_dict[0]))
