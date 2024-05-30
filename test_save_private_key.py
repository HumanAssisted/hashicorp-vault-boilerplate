import os
import hvac
import unittest

# Set the VAULT_ADDR environment variable
os.environ['VAULT_ADDR'] = 'http://127.0.0.1:8300'

# Use the root token for authentication
root_token = 'root'

def save_private_key(user_id: str, encrypted_key: str):
    # Initialize the HVAC client with the root token
    client = hvac.Client(token=root_token)

    # Construct the Vault path using the user_id
    path = f'secret/user_keys/{user_id}'

    # Use the HVAC client to store the encrypted key in Vault
    client.secrets.kv.v2.create_or_update_secret(path=path, secret={'key': encrypted_key})

    print(f"Encrypted key for user_id {user_id} saved successfully.")

def retrieve_private_key(user_id: str) -> str:
    # Initialize the HVAC client with the root token
    client = hvac.Client(token=root_token)

    # Construct the Vault path using the user_id
    path = f'secret/user_keys/{user_id}'

    try:
        # Use the HVAC client to retrieve the encrypted key from Vault
        result = client.secrets.kv.v2.read_secret_version(path=path)
        return result['data']['data']['key']
    except hvac.exceptions.InvalidPath:
        print(f"No key found for user_id {user_id}")
        return ""

def write_system_secret(secret_name: str, secret_value: str):
    # Initialize the HVAC client with the root token
    client = hvac.Client(token=root_token)

    # Construct the Vault path using the secret_name
    path = f'secret/data/system_secrets/{secret_name}'
    print(f"Constructed path: {path}")

    # Use the HVAC client to store the secret value in Vault
    try:
        response = client.secrets.kv.v2.create_or_update_secret(path=path, secret={'value': secret_value})
        print(f"Response from Vault: {response}")
    except hvac.exceptions.Forbidden as e:
        print(f"Permission denied error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    print(f"System secret for secret_name {secret_name} saved successfully.")

def retrieve_system_secret(secret_name: str) -> str:
    # Initialize the HVAC client with the root token
    client = hvac.Client(token=root_token)

    # Construct the Vault path using the secret_name
    path = f'secret/data/system_secrets/{secret_name}'

    try:
        # Use the HVAC client to retrieve the secret value from Vault
        result = client.secrets.kv.v2.read_secret_version(path=path)
        secret_value = result['data']['data']['value']
        os.environ[secret_name] = secret_value
        return secret_value
    except hvac.exceptions.InvalidPath:
        print(f"No secret found for secret_name {secret_name}")
        return ""

# Unit tests for the functions
class TestVaultFunctions(unittest.TestCase):

    def test_save_private_key(self):
        user_id = "test_user"
        encrypted_key = "test_encrypted_key"
        save_private_key(user_id, encrypted_key)
        # Verify that the key was saved correctly
        client = hvac.Client(token=root_token)
        path = f'secret/user_keys/{user_id}'
        result = client.secrets.kv.v2.read_secret_version(path=path)
        self.assertEqual(result['data']['data']['key'], encrypted_key)

    def test_retrieve_private_key(self):
        user_id = "test_user"
        encrypted_key = "test_encrypted_key"
        save_private_key(user_id, encrypted_key)
        key = retrieve_private_key(user_id)
        self.assertEqual(key, encrypted_key)

    def test_write_system_secret(self):
        secret_name = "test_secret"
        secret_value = "test_value"
        write_system_secret(secret_name, secret_value)
        # Verify that the secret was saved correctly
        client = hvac.Client(token=root_token)
        path = f'secret/data/system_secrets/{secret_name}'
        result = client.secrets.kv.v2.read_secret_version(path=path)
        self.assertEqual(result['data']['data']['value'], secret_value)

    def test_retrieve_system_secret(self):
        secret_name = "test_secret"
        secret_value = "test_value"
        write_system_secret(secret_name, secret_value)
        retrieved_value = retrieve_system_secret(secret_name)
        self.assertEqual(retrieved_value, secret_value)
        self.assertEqual(os.environ[secret_name], secret_value)

if __name__ == "__main__":
    unittest.main()
