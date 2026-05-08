from checkCardPIN import generateCardPINFunc, parse_card_key
import json
# Generate a card PIN
# option = 0: only this UID is valid
# option = 1: the PIN for all UIDs are valid
# option = 2: the PIN for all UIDs are valid, you can add other usage scenarios
# if option = 0, the decoded UID will be a random 8-digit number
# if option = 1 or 2, the decoded UID will be the same as the input UID
priceLevel = 100
uid = "12345678"
option = 1


if option == 0:
    optionContent = "only this UID is valid"
elif option == 1:
    optionContent = "the PIN for all UIDs are valid"
elif option == 2:
    optionContent = "the PIN for all UIDs are valid, you can add other usage scenarios"

def genMuti(a):
    print("---------------------------")
    print("生成卡密数量: " + str(a))
    cardPIN = []
    for i in range(a):
        # 生成卡密
        cardPINtemp = generateCardPINFunc(priceLevel, uid, option)
        cardPIN.append(cardPINtemp[1])
        # print("copy this to the cardPIN.json: " + str(cardPINtemp[1]))

        # 解密卡密，确保正确
        parsed_uid, parsed_price = parse_card_key(cardPINtemp[1])
        print("parsed uid:", parsed_uid, "price:", parsed_price)
        print("-----------")
        # opt0Str = "3408"
        # opt1Str = "8196"
        # opt2Str = "5072"
    cardPIN = (
        json.dumps(cardPIN)
        .replace("[", "")
        .replace("]", "")
        .replace(",", ",\n")
        .replace(" ", "")
    )
    print("---------------------------")
    print("本次生成的卡密价格: " + str(priceLevel))
    print("本次生成的卡密option：" + str(optionContent))
    print("复制到cardPIN.json: \n--------\n" + cardPIN)

# 需要生成的数量
genMuti(10)
