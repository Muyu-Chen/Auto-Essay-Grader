import json
import random
import string

### IMPORTANT ###
# DO NOT SHARE THIS `CHARSET` WITH ANYONE
# you need to fill this with 36 characters in random order
# you cannot repeat characters
# this is the key for encoding and decoding the UID
# so make sure you don't lose it and don't share it.
SHUFFLED_CHARSET = "1234567890abcdefghijklmnopqrstuvwxyz"
# the string before the UID is used to determine the validity of the UID
# also for the security of the card PIN, you can change it
opt0Str = "1234"
opt1Str = "2234"
opt2Str = "3234"

def custom_encode_uid(uid):
    # Custom compact encoding: Encode a 12-digit number into an 8-character string using a shuffled base-36 encoding
    uid_num = int(uid)  # Ensure UID is a number
    encoded = ""
    base = len(SHUFFLED_CHARSET)
    while uid_num > 0:
        encoded = SHUFFLED_CHARSET[uid_num % base] + encoded
        uid_num //= base
    return encoded.rjust(8, "0")  # Pad with zeros to 8 characters


def custom_decode_uid(encoded_uid):
    # decode: Convert the 8-character string back to a 12-digit number
    base = len(SHUFFLED_CHARSET)
    uid_num = 0
    for char in encoded_uid:
        uid_num = uid_num * base + SHUFFLED_CHARSET.index(char)
    return str(uid_num).zfill(12)  # Pad with zeros to 12 digits


def generate_card_key(price, uid):
    # Define the mapping between price and checksum characters
    price = str(price)
    price_map = {
        "5": "a",
        "10": "b",
        "20": "c",
        "30": "d",
        "50": "e",
        "100": "f",
        "type1": "g",
        "type2": "h",
        "type3": "i",
        "type4": "j",
    }

    if price not in price_map:
        raise ValueError(
            f"Unsupported price: {price}. Supported prices are {list(price_map.keys())}"
        )

    # Encode UID
    uid_encoded = custom_encode_uid(uid)

    # Construct the specific digits of the card PIN
    card_parts = list(uid_encoded)  # 1st, 3rd, 5th, 7th, 9th, 11th, 13th, 15th positions


    # You can change the position of the random, price and category characters
    # Fill random characters into 2nd, 4th, 6th, and 8th positions
    for i in range(1, 8, 2):
        card_parts.insert(i, random.choice(string.digits))

    # Add the 10th and 12th positions with the price corresponding category character
    card_parts.insert(9, price_map[price])
    card_parts.insert(11, random.choice(string.ascii_letters))

    # Add the 14th checksum character (simple example: random letter)
    checksum = random.choice(string.ascii_letters + string.digits)
    card_parts.insert(13, checksum)

    return "".join(card_parts)


def parse_card_key(card_key):
    # Define the reverse mapping of checksum characters to prices
    reverse_price_map = {
        "a": "5",
        "b": "10",
        "c": "20",
        "d": "30",
        "e": "50",
        "f": "100",
        "g": "type1",
        "h": "type2",
        "i": "type3",
        "j": "type4",
    }

    # decode UID
    uid_encoded = "".join([card_key[i] for i in range(0, 16, 2)])
    uid = custom_decode_uid(uid_encoded)

    # Extract the price category character and parse the price
    price_char = card_key[9]
    if price_char not in reverse_price_map:
        raise ValueError(f"Invalid card key: {card_key}. Cannot determine price.")

    price = reverse_price_map[price_char]

    return uid, price


def checkCardPINFunc(cardPIN):
    try:
        parsed_uid, parsed_price = parse_card_key(cardPIN)
    except Exception as e:
        return -1, str(e)

    print(f"Parsed UID: {parsed_uid}")
    value3 = 0
    print(f"Parsed price: {parsed_price}")
    if parsed_uid[0:4] == opt0Str:
        # only this UID is valid
        value1 = 0
        value3 = parsed_uid[4:12]
    elif parsed_uid[0:4] == opt1Str:
        # all UIDs are valid
        value1 = 1
    elif parsed_uid[0:4] == opt2Str:
        # all UIDs are invalid, special case
        value1 = 2
    else:
        return -1, "Invalid PIN", 0
    print(f"Parsed price: {parsed_price}")
    value2 = -1
    # check if the card PIN is in the database
    with open("cardPin.json", "r") as f:
        data = json.load(f)
    dataPrice = data.get(str(parsed_price))  
    # Assume price_level is the price level you determined earlier
    if dataPrice:
        for pin in dataPrice:
            if pin == cardPIN:
                value2 = 0
                # delete the card PIN from the database
                dataPrice.remove(pin)
                data[str(parsed_price)] = dataPrice
                with open("cardPin.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=4)
                break
    if value2 == -1:
        return -1, "Invalid PIN", 0
    return value1, parsed_price, value3


def generateCardPINFunc(price, uid, option):
    # option = 1: only this UID is valid
    # option = 2: all UIDs are valid
    if len(str(uid)) != 8:
        return -1, "Invalid UID"
    uid = int(uid)
    if option == 0:
        strbefore = opt0Str
    elif option == 1:
        strbefore = opt1Str
        uid = "".join([str(random.randint(0, 9)) for _ in range(8)])
    elif option == 2:
        strbefore = opt2Str
    else:
        return -1, "Invalid option"

    uid = strbefore + str(uid)
    try:
        card_key = generate_card_key(str(price), uid)
    except Exception as e:
        return -1, str(e)

    print(f"Generated card key: {card_key}")
    return 0, card_key


# example
# if __name__ == "__main__":
#     uid = "000019200001"
#     price = "20"

#     # generate card key
#     card_key = generate_card_key(price, uid)
#     print(f"Generated card key: {card_key}")

#     # parse card key
#     parsed_uid, parsed_price = parse_card_key(card_key)
#     print(f"Parsed UID: {parsed_uid}")
#     print(f"Parsed price: {parsed_price}")
