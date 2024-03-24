
def encrypt(name: str, age: int, hobbies: list):
    encryptedText = []
    encryptedName = encrypt_text(name)
    encryptedAge = encrypt_number(age)
    encryptedHobbies = [encrypt_text(hobby) for hobby in hobbies]

    encryptedText.extend([encryptedName, encryptedAge])
    encryptedText.extend(encryptedHobbies)

    return encryptedText


def encrypt_text(text):
    encrypted_text = ""



    return encrypted_text


def encrypt_number(number: int):
    return number + 132947624


print(encrypt("ABCD", 16, ["coding"])[0])
