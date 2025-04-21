import os
import hashlib
import binascii

password = input("password: ")

salt = os.urandom(16)
hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)

salt_hex = binascii.hexlify(salt).decode()
hash_hex = binascii.hexlify(hashed).decode()

with open("hash_salt.txt", "w") as file:
    file.write(hash_hex + "\n")
    file.write(salt_hex)

print("hashed password:", hash_hex)
print("salt:", salt_hex)
print("saved to file!")
