from binascii import unhexlify

from substrateinterface import Keypair

def verify_signature(hotkey: str, message: str, signature: str) -> bool:
    try:
        keypair = Keypair(ss58_address=hotkey, ss58_format=42)
        real_signature = unhexlify(signature.encode())
        return keypair.verify(data=message, signature=real_signature)
    
    except Exception as e:
        return False
