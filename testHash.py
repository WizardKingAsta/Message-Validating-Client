import hashlib

# 94116ce41c9d0bab6e3934e 8575cffd63d6f059bc04b0369ab767aaba38289e4 / server.py
# 94116ce41c9d0bab6e3934e dfc3ce4e0ad6f059bc04b0369a12e34aba38289e4 / expected
# 94116ce41c9d0bab6e3934e 8575cffd63d6f059bc04b0369ab767aaba38289e4 / testHash

def main():
    
    message = "Imagine IP addresses are like phone numbers, but for machines instead of humans. Can you imagine sending a text to 192.168.1.1 saying, 'Hey, it's your router, let's catch up."
    key = "5fe9a3d2fbc04e7199828f15ed6cbf0f"
    
    expected = "94116ce41c9d0bab6e3934edfc3ce4e0ad6f059bc04b0369a12e34aba38289e4"
    
    
    hasher = hashlib.sha256()
    
    print(f"Adding message to hash: {message}")
    hasher.update(message.encode("ascii"))
    
    print(f"Adding key to hash: {key}")
    hasher.update(key.encode('ascii'))
    
    signature = hasher.hexdigest()
    
    # print(f"Signature: {signature}")
    
    if signature == expected:
        print("Match!")
    else:
        print("Generated signature does not match expected")
        print(f"Generated: {signature}")
        print(f"Expected:  {expected}")
    
if __name__ == "__main__":
    main()