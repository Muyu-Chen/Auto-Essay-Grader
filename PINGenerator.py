from checkCardPIN import generateCardPINFunc, parse_card_key

# Generate a card PIN
# option = 0: only this UID is valid
# option = 1: the PIN for all UIDs are valid
# option = 2: the PIN for all UIDs are valid, you can add other usage scenarios
# if option = 0, the decoded UID will be a random 8-digit number
# if option = 1 or 2, the decoded UID will be the same as the input UID
priceLevel = 100
uid = "12345678"
option = 1
cardPIN = generateCardPINFunc(priceLevel, uid, option)
print("copy this to the cardPIN.json : " + str(cardPIN[1]))
# decode
parsed_uid, parsed_price = parse_card_key(cardPIN[1])
print(parsed_uid)
