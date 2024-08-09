import random as rng

maj = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
minuscules = "abcdefghijklmnopqrstuvwxyz"
chiffres = "0123456789"

types = [maj, minuscules, chiffres]
typeChar = [maj, minuscules]

def generate():
	code = ""
	for i in range(6):
		choixType = rng.choice(types)
		code += rng.choice(choixType)

	return code