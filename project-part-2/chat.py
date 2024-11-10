#!/usr/bin/env python3

import socket
import threading
import rsa
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# setting up the RSA ecryption keys used in the key exchange
public_key, private_key = rsa.newkeys(1024)

# the RSA key of the other client in the chat 
public_partner_key = None

# the aes cypher used to encrypt the messages
cipher = None
aes_key = None

client_mode = input("Do you want to host a chat (1), or connect to a chat (2)? ")

if client_mode == "1":
    host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host.bind(("localhost", 9998))
    host.listen()

    client, _ = host.accept()
    client.send(public_key.save_pkcs1("PEM"))
    public_partner_key = rsa.PublicKey.load_pkcs1(client.recv(1024))
    
    # setting up the AES keys and  cypher to encrypt the messages
    aes_key = get_random_bytes(16)
    cipher = AES.new(aes_key, AES.MODE_OCB)
    
    client.send(rsa.encrypt(aes_key, public_partner_key))

elif client_mode == "2":
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("localhost", 9998))
    
    # receiving the hosts public key and sending its own for RSA encryption
    public_partner_key = rsa.PublicKey.load_pkcs1(client.recv(1024))
    client.send(public_key.save_pkcs1("PEM"))
    
    # receiving the AES key and decrypting using RSA
    aes_key = rsa.decrypt(client.recv(1024), private_key)
    cipher = AES.new(aes_key, AES.MODE_OCB) 
else:
    exit()

def send_messages(client):
    print("Chat connected!")
    while True:
        message = input("")
        ciphertext, tag = cipher.encrypt_and_digest(message.encode())
        encrypted = tag + cipher.nonce + ciphertext
        client.send(encrypted)
        print("You: " + message)

def receive_messages(client):
    while True:
        encrypted = client.recv(1024)
        tag = encrypted[:16]
        nonce = encrypted[16:31]
        ciphertext = encrypted[31:]
        cipher = AES.new(aes_key, AES.MODE_OCB, nonce=nonce)
        try:
            message = cipher.decrypt_and_verify(ciphertext, tag)
        except ValueError:
            print("A received message has been tampered with!!")
            sys.exit(1)
        print("Partner: " + message.decode())


threading.Thread(target=send_messages, args=(client,)).start()
threading.Thread(target=receive_messages, args=(client,)).start()


