use serde::{Deserialize, Serialize};
use vaultrs::client::{VaultClient, VaultClientSettingsBuilder};
use vaultrs::kv2;
use vaultrs::auth::approle;
use vaultrs::error::ClientError;

#[derive(Debug, Deserialize, Serialize)]
struct MySecret {
    password: String,
}

#[tokio::main]
async fn main() -> Result<(), ClientError> {
    // AppRole credentials
    let role_id = "fd62632b-ac20-9ee4-4678-2b55750267da";
    let secret_id = "e9d690d7-6fcc-72a1-7948-b9773bb4a9d0";

    // Create a Vault client without a token
    let client = VaultClient::new(
        VaultClientSettingsBuilder::default()
            .address("http://127.0.0.1:8300")
            .build()
            .unwrap(),
    )
    .unwrap();

    // Log in with AppRole to get a token
    let login_response = approle::login(&client, role_id, secret_id).await?;
    let token = login_response.client_token;

    // Create a new client with the obtained token
    let client = VaultClient::new(
        VaultClientSettingsBuilder::default()
            .address("http://127.0.0.1:8300")
            .token(&token)
            .build()
            .unwrap(),
    )
    .unwrap();

    // Retrieve the secret
    let secret: MySecret = kv2::read(&client, "secret", "mysecret").await.unwrap();
    println!("Retrieved password: {}", secret.password);

    Ok(())
}
