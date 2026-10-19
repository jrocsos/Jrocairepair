#!/usr/bin/env python3
import os
import struct
import hashlib
import sys

def extract_passcode_hash(backup_path):
    """
    Extracts the passcode hash from an iOS backup's 'Status.plist' 
    or 'Keychain.plist' if available.
    Note: Modern iOS encrypts this, so this often requires a jailbreak 
    or a previously decrypted backup.
    """
    # Path to the keychain database in a decrypted backup
    keychain_db = os.path.join(backup_path, "Protected", "com.apple.Keychain")
    
    if not os.path.exists(keychain_db):
        print("[-] Keychain database not found. Ensure backup is decrypted.")
        return None

    try:
        # Read the binary data (simplified structure)
        with open(keychain_db, 'rb') as f:
            data = f.read()
        
        # Locate the specific UUID entry for the passcode
        # This is a simplified regex-style search for demo purposes
        # In reality, you parse the SQLite or binary plist format
        import sqlite3
        conn = sqlite3.connect(keychain_db)
        cursor = conn.cursor()
        
        # Query the key-value store for 'kSecValueData' related to passcode
        cursor.execute("SELECT value FROM key_value_store WHERE key LIKE '%passcode%'")
        row = cursor.fetchone()
        
        if row:
            hash_data = row[0]
            print(f"[+] Extracted Passcode Hash: {hash_data.hex()}")
            return hash_data
        else:
            print("[-] No passcode hash found in backup.")
            
    except Exception as e:
        print(f"[-] Error extracting hash: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python extract_ios_hash.py <backup_path>")
        sys.exit(1)
    
    extract_passcode_hash(sys.argv[1])