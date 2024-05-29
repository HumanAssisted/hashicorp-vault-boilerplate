# HashiCorp Vault with Rust Client Libraries

## Overview
This project demonstrates how to set up HashiCorp Vault using Docker Compose for local development and Kubernetes for production. It also includes a Rust client that interacts with Vault to retrieve secrets and implements cloud-neutral authentication using AppRole.

## Local Development Setup with Docker Compose
1. Create a `docker-compose.yml` file with the following content:
    ```yaml
    version: '3'
    services:
      vault:
        image: hashicorp/vault:1.13.3
        container_name: vault
        ports:
          - "8300:8300"
        environment:
          VAULT_DEV_ROOT_TOKEN_ID: "root"
          VAULT_ADDR: "http://0.0.0.0:8300"
        volumes:
          - ./vault/config:/vault/config
    ```

2. Create a `config.hcl` file in the `vault/config` directory:
    ```hcl
    storage "file" {
      path = "/vault/file"
    }
    listener "tcp" {
      address = "0.0.0.0:8300"
      tls_disable = 1
    }
    ui = true
    ```

3. Run `docker-compose up` to start Vault.

## Production Deployment on Kubernetes
### AWS (EKS)
1. Install and configure the AWS CLI.
2. Create an EKS cluster:
    ```shell
    aws eks create-cluster --name my-cluster --role-arn <role-arn> --resources-vpc-config subnetIds=<subnet-ids>,securityGroupIds=<security-group-ids>
    ```

3. Update `kubectl` configuration for EKS:
    ```shell
    aws eks update-kubeconfig --name my-cluster
    ```

4. Apply the Vault ConfigMap and Deployment manifests:
    ```shell
    kubectl apply -f vault-config.yaml
    kubectl apply -f vault-deployment.yaml
    ```

5. Check the deployment status:
    ```shell
    kubectl get pods -l app=vault
    ```

6. Port forward to access the Vault UI:
    ```shell
    kubectl port-forward service/vault 8300:8300
    ```

### GCP (GKE)
1. Install and configure the GCP SDK.
2. Create a GKE cluster:
    ```shell
    gcloud container clusters create my-cluster --zone <zone>
    ```

3. Update `kubectl` configuration for GKE:
    ```shell
    gcloud container clusters get-credentials my-cluster --zone <zone>
    ```

4. Apply the Vault ConfigMap and Deployment manifests:
    ```shell
    kubectl apply -f vault-config.yaml
    kubectl apply -f vault-deployment.yaml
    ```

5. Check the deployment status:
    ```shell
    kubectl get pods -l app=vault
    ```

6. Port forward to access the Vault UI:
    ```shell
    kubectl port-forward service/vault 8300:8300
    ```

## Rust Client Libraries
1. Add dependencies to `Cargo.toml`:
    ```toml
    [dependencies]
    vaultrs = { version = "0.7.1", default-features = false, features = ["native-tls"] }
    tokio = { version = "1", features = ["full"] }
    openssl = "0.10.64"
    hyper-openssl = "0.10.2"
    serde = { version = "1.0", features = ["derive"] }
    ```

2. Example Rust code to retrieve secrets:
    ```rust
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
    ```

## Best Practices
1. Use environment variables for sensitive information.
2. Regularly rotate secrets and credentials.
3. Apply least privilege principle for access controls.
4. Monitor and audit access to Vault.
5. Ensure proper network security configurations.

## Prerequisites
1. Ensure Docker and Kubernetes are installed and configured.
2. Set up AWS or GCP credentials if deploying on those platforms.
3. Obtain access to the HashiCorp Vault Docker image.
4. Familiarize with Rust and the `vaultrs` library.
5. Prepare necessary configuration files and manifests.
