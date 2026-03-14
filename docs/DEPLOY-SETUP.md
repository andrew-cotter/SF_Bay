# Production deploy: auto build and deploy on push

Every push to the **main** branch triggers a GitHub Actions workflow that:

1. Builds the Docker image
2. Pushes it to **Amazon ECR**
3. SSHs into your EC2 instance, pulls the new image, and restarts the app

Do this **one-time setup** in AWS and GitHub, then pushes to `main` will deploy automatically.

---

## 1. Create an ECR repository (AWS Console)

1. Open **Amazon ECR** in the AWS Console (same region as your EC2, e.g. **us-east-2**).
2. **Create repository**.
3. Repository name: **`baytemps`** (or change `ECR_REPOSITORY` in `.github/workflows/deploy.yml` to match).
4. Leave other settings default → **Create repository**.
5. Note the **URI** (e.g. `123456789012.dkr.ecr.us-east-2.amazonaws.com/baytemps`). You’ll need the registry part (`123456789012.dkr.ecr.us-east-2.amazonaws.com`) and the repo name for GitHub.

---

## 2. Allow EC2 to pull from ECR (IAM)

The EC2 instance needs permission to pull images from your ECR repo.

1. Open **IAM** → **Roles** → select the role attached to your EC2 instance.
2. **Add permissions** → **Create inline policy** (or attach **AmazonEC2ContainerRegistryReadOnly** if you’re fine with read-only to all your ECR repos).
3. For a minimal custom policy, use:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage",
        "ecr:BatchCheckLayerAvailability"
      ],
      "Resource": "arn:aws:ecr:REGION:ACCOUNT_ID:repository/baytemps"
    }
  ]
}
```

Replace `REGION` and `ACCOUNT_ID` with your ECR region and AWS account ID. Name the policy (e.g. `ECR-Pull-Baytemps`) and save.

---

## 3. Create a user (or use existing) for GitHub Actions (IAM)

GitHub Actions needs AWS credentials to push to ECR and (optionally) to run the deploy. Create an IAM user used only for CI:

1. **IAM** → **Users** → **Create user** (e.g. `github-actions-baytemps`). No console login needed.
2. **Attach policies** → **Create policy** (or use existing). The user needs:
   - **Push to ECR**: `ecr:GetAuthorizationToken` (resource `*`) and, for the repo, `ecr:BatchCheckLayerAvailability`, `ecr:GetDownloadUrlForLayer`, `ecr:BatchGetImage`, `ecr:PutImage`, `ecr:InitiateLayerUpload`, `ecr:UploadLayerPart`, `ecr:CompleteLayerUpload`.
   - Or attach **AmazonEC2ContainerRegistryPowerUser** (or a custom policy scoped to the `baytemps` repo) so the workflow can push images.

3. **Create access key** for this user → **Application running outside AWS** → create key. Copy the **Access key ID** and **Secret access key**; you’ll add them as GitHub secrets.

---

## 4. Add GitHub secrets

In your GitHub repo: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**. Add:

| Secret name               | Description |
|---------------------------|-------------|
| `AWS_ACCESS_KEY_ID`       | IAM user access key from step 3. |
| `AWS_SECRET_ACCESS_KEY`   | IAM user secret key from step 3. |
| `AWS_REGION`              | ECR and EC2 region, e.g. `us-east-2`. |
| `EC2_HOST`                | EC2 public IP or DNS (e.g. `18.116.204.200`). |
| `EC2_SSH_PRIVATE_KEY`     | Full contents of your `.pem` file (the private key you use for `ssh -i ...`). |
| `SECRET_ID`               | Secrets Manager secret name (e.g. `mysql_secret`). |

**EC2_SSH_PRIVATE_KEY:** Open your `.pem` in a text editor and paste the entire contents (including `-----BEGIN ... KEY-----` and `-----END ... KEY-----`) into the secret value.

If your AMI uses **Ubuntu**, the workflow uses `ec2-user` by default; change the workflow’s `username` to `ubuntu` under the “Deploy to EC2” step, or add a secret like `EC2_USERNAME` and use it in the workflow.

---

## 5. Ensure the startup script and directory exist on EC2

The workflow runs `/opt/baytemps/ec2-start-baytemps.sh` on the instance. From the [EC2 setup walkthrough](EC2-SETUP-WALKTHROUGH.md), you should already have:

- `/opt/baytemps/ec2-start-baytemps.sh` (executable)
- Directory owned by `ec2-user`: `sudo chown -R ec2-user:ec2-user /opt/baytemps`

If not, copy the script from the repo and run the `chmod` and `chown` steps from the walkthrough.

---

## 6. Push to main

Push (or merge) to the **main** branch. The **Build and deploy** workflow will run. You can watch it under **Actions** in GitHub. When it finishes, the app on EC2 will be running the new image.

---

## Optional: Deploy from a different branch

Edit `.github/workflows/deploy.yml` and change:

```yaml
on:
  push:
    branches: [main]
```

to your branch name (e.g. `branches: [production]`).

---

## Optional: Use GitHub OIDC instead of access keys

You can avoid storing `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` by using [OpenID Connect (OIDC)](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services). That requires configuring an IAM OIDC identity provider and a role that the workflow assumes. The workflow would then use `aws-actions/configure-aws-credentials@v4` with `role-to-assume` instead of access keys. If you want to switch to OIDC later, we can adapt the workflow and IAM steps.
