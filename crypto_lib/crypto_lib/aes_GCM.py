from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
from Cryptodome.Protocol.KDF import scrypt

password = b's3kr3tp4ssw0rd'

def _get_secret_key(salt):
    secretKey = scrypt(password=password, salt=salt, key_len=16,N=2**14,r=8,p=1) # type: ignore
    key: bytes
    if isinstance(secretKey, tuple):
        key = secretKey[0]
    elif isinstance(secretKey, bytes):
        key = secretKey
    else:
        raise
    return key

def _get_secret_key_and_salt():
    kdf_salt = get_random_bytes(16)
    key = _get_secret_key(salt=kdf_salt)
    return key, kdf_salt

def _get_secret_key_from_salt(kdf_salt):
    key = _get_secret_key(salt=kdf_salt)
    return key

def encrypt_AES_GCM(data):
    """encrypt the plain text

    Args:
        data (str): data as plain string

    Returns:
      tuple
      [bytes, bytes, Buffer, bytes]  : kdf_salt, ciphertext, nonce, auth_tag
    """
    try:
        key, kdf_salt = _get_secret_key_and_salt()
        aes_cipher = AES.new(key, AES.MODE_GCM)
        ciphertext, auth_tag = aes_cipher.encrypt_and_digest(data)
        return (kdf_salt, ciphertext, aes_cipher.nonce, auth_tag)
    except:
        raise

def decrypt_AES_GCM(kdf_salt, ciphertext, nonce, auth_tag):
    """decrypt the cipher text

    Args:
        kdf_salt (byte): the salt used for encyption
        ciphertext (byte): the encypted text
        nonce (byte): the nonce created while encryption
        auth_tag (byte): the auth_tag created while encryption

    Returns:
        bytes: the decrypted plain text
    """
    try:
        key = _get_secret_key_from_salt(kdf_salt=kdf_salt)
        aes_cipher = AES.new(key, AES.MODE_GCM, nonce)
        plaintext = aes_cipher.decrypt_and_verify(ciphertext, auth_tag)
        return plaintext
    except:
        raise

#kdf_salt, ciphertext, nonce, auth_tag  = encryptedMsg