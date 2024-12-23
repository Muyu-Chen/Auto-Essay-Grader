from checkCardPIN import generateCardPINFunc, parse_card_key

# Generate a card PIN
# option = 1: only this UID is valid
# option = 2: all UIDs are valid
# option = 3: all UIDs are invalid
# if option = 0, the decoded UID will be a random 8-digit number
# if option = 1 or 2, the decoded UID will be the same as the input UID
cardPIN = generateCardPINFunc(100, "12345678", 0)
print(cardPIN[1])
# decode
parsed_uid, parsed_price = parse_card_key(cardPIN[1])
print(parsed_uid)
