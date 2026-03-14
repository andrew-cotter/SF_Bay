/Users/andrewcotter/Downloads/baytemps-keypair.pem ec2-user@18.116.204.200

# EC2 setup walkthrough (step by step)

This guide gets the Bay temps app running on your EC2 instance **with** your MySQL credentials coming from AWS Secrets Manager. No secrets in code or on disk that you have to edit by hand.

---

## Why the app breaks without secrets.toml

- The app connects to MySQL using `st.connection("mysql", ...)`, which reads from a file: **`.streamlit/secrets.toml`**.
- That file is **not** in the Docker image (it’s ignored so we don’t put real passwords in the image).
- When the container **starts**, the **entrypoint** can **create** that file — but only if it sees **environment variables** like `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, etc.
- So we need to: **get the secret from AWS → turn it into env vars → run the container with those env vars**. Then the entrypoint writes `secrets.toml` inside the container and the app works.

The script in this repo does exactly that: it fetches the secret, writes an env file, and runs Docker with that env file.

---

## What you need before starting

- An **EC2 instance** (you have this).
- The instance has an **IAM role** that can read your MySQL secret in Secrets Manager (you have this).
- You know:
  - The **name** of the secret in AWS (e.g. `my-mysql-credentials`).
  - The **AWS region** where the secret lives (e.g. `us-east-1`).
- The **Docker image** for this app. Either you’ll build it on the instance or pull it from ECR; we’ll do that in the steps below.

---

## Step 1: Connect to your EC2 instance

From your own computer (Terminal or PowerShell), SSH in. You need the key you used when creating the instance and the instance’s public IP or hostname.

**Example (replace the key path and address):**

```bash
ssh -i /path/to/your-key.pem ec2-user@YOUR_EC2_PUBLIC_IP
```

- Amazon Linux often uses user **`ec2-user`**.
- Ubuntu often uses user **`ubuntu`**.

If you’re in, you’ll see a prompt like `[ec2-user@ip-172-31-… ~]$`. The rest of the steps are run **on this SSH session** (on the EC2 instance).

---

## Step 2: Install Docker and jq (if not already there)

The script needs **Docker** (to run the app container) and **jq** (to read the JSON secret). Run these and wait for them to finish.

**On Amazon Linux 2023:**

```bash
sudo yum update -y
sudo yum install -y docker jq
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ec2-user
```

Then **log out and log back in** over SSH (so your user is in the `docker` group):

```bash
exit
```

Then SSH in again:

```bash
ssh -i /path/to/your-key.pem ec2-user@YOUR_EC2_PUBLIC_IP
```

**On Ubuntu:**

```bash
sudo apt update
sudo apt install -y docker.io jq
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ubuntu
```

Again, log out and back in over SSH after `usermod`.

---

## Step 3: Put the startup script on the instance

You need the script **`scripts/ec2-start-baytemps.sh`** from this repo on the EC2 instance. Two ways:

**Option A – Copy from your computer (recommended)**

On **your own machine** (in a new terminal, not in SSH), from the folder that contains the SF_Bay repo:

```bash
scp -i /path/to/your-key.pem scripts/ec2-start-baytemps.sh ec2-user@YOUR_EC2_PUBLIC_IP:/tmp/ec2-start-baytemps.sh
```

Then on the **EC2 instance** (in your SSH session):

```bash
sudo mkdir -p /opt/baytemps
sudo mv /tmp/ec2-start-baytemps.sh /opt/baytemps/
sudo chmod +x /opt/baytemps/ec2-start-baytemps.sh
sudo chown -R ec2-user:ec2-user /opt/baytemps
```

(The last line makes your user the owner of `/opt/baytemps` so the script can write `mysql.env` there. On Ubuntu use `ubuntu` instead of `ec2-user`.)

**Option B – Create the file by hand on EC2**

On the EC2 instance:

```bash
sudo mkdir -p /opt/baytemps
sudo nano /opt/baytemps/ec2-start-baytemps.sh
```

Paste the **entire contents** of `scripts/ec2-start-baytemps.sh` from the repo, save (Ctrl+O, Enter, then Ctrl+X). Then:

```bash
sudo chmod +x /opt/baytemps/ec2-start-baytemps.sh
sudo chown -R ec2-user:ec2-user /opt/baytemps
```

(On Ubuntu use `ubuntu` instead of `ec2-user`.)

---

## Step 4: Get the Docker image on the instance

The script will run a container from an image named **`baytemps:latest`** by default. So the instance must have that image.

**If you build the image on this EC2 instance:**

- Install git if needed (Amazon Linux: `sudo yum install -y git`), then clone the repo and build:

```bash
sudo yum install -y git
cd /tmp
git clone https://github.com/YOUR_USERNAME/SF_Bay.git
cd SF_Bay
docker build -t baytemps:latest .
```

Replace `YOUR_USERNAME/SF_Bay` with your actual repo URL. Ensure `up_to_2024.csv` is committed and pushed so the build has the data file.

- Or copy the repo with `scp` from your Mac (no git on EC2 needed); see the troubleshooting section if the image is missing.

(You need the Dockerfile and app code there; the Dockerfile is in the repo root.)

**If the image is in Amazon ECR:**

- Log in and pull (replace region and ECR URI with yours):

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com
docker pull 123456789012.dkr.ecr.us-east-1.amazonaws.com/baytemps:latest
docker tag 123456789012.dkr.ecr.us-east-1.amazonaws.com/baytemps:latest baytemps:latest
```

Then the script’s default `baytemps:latest` will work.

---

## Step 5: Run the script (this creates secrets and starts the app)

On the EC2 instance, run the script **once**. You must tell it the **name of your secret** and the **region**.

Replace:

- **`your-secret-name`** with the real name of your MySQL secret in AWS (e.g. `prod/mysql/baytemps`).
- **`us-east-1`** with the region where that secret lives.

**Run:**

```bash
cd /opt/baytemps
SECRET_ID=your-secret-name AWS_REGION=us-east-1 ./ec2-start-baytemps.sh
```

If your instance needs `sudo` to run Docker:

```bash
DOCKER_CMD=sudo docker SECRET_ID=your-secret-name AWS_REGION=us-east-1 ./ec2-start-baytemps.sh
```

What this does:

1. Fetches the secret from Secrets Manager.
2. Writes `/opt/baytemps/mysql.env` with `MYSQL_HOST`, `MYSQL_USER`, `MYSQL_PASSWORD`, etc.
3. Starts a container with `--env-file /opt/baytemps/mysql.env`. The container’s entrypoint sees those env vars and **creates** `.streamlit/secrets.toml` inside the container, so the app stops breaking.

---

## Step 6: Check that it’s running

- List containers:

```bash
docker ps
```

You should see a container named **`baytemps`** with port **8501** mapped.

- From your **browser**, open:

**`http://YOUR_EC2_PUBLIC_IP:8501`**

You should see the Bay temps dashboard. If it loads but MySQL data is missing, check that the secret’s JSON has the keys the script expects: `host`, `port`, `username`, `password`, `database`. If your secret uses different key names, see the script’s comments for the `SECRET_KEY_*` variables.

- Make sure the EC2 **security group** allows **inbound** traffic on port **8501** from your IP (or from anywhere if you’re okay with that for now).

---

## If something goes wrong

- **“SECRET_ID or first argument required”**  
  You didn’t set `SECRET_ID`. Run again with  
  `SECRET_ID=your-secret-name AWS_REGION=us-east-1 ./ec2-start-baytemps.sh`

- **“Access Denied” or permission errors from AWS**  
  The instance’s IAM role doesn’t have `secretsmanager:GetSecretValue` for that secret. Add a policy that allows it and attach it to the instance role.

- **“jq: command not found”**  
  Install jq (Step 2).

- **“docker: command not found” or “permission denied” for Docker**  
  Install Docker and add your user to the `docker` group, then log out and back in (Step 2). Or use `DOCKER_CMD=sudo docker` when running the script.

- **Container exits immediately / app still says no secrets**  
  Check the container logs:  
  `docker logs baytemps`  
  If the entrypoint doesn’t see `MYSQL_HOST`, it won’t write `secrets.toml`. Make sure the script ran without errors and that the secret’s JSON has the expected keys so the env file is correct.

---

## Running the script again after a reboot (optional)

The script starts the container with `--restart unless-stopped`, so Docker will usually start the container again after a reboot. The env file at `/opt/baytemps/mysql.env` is still there.

If you ever need to **restart** the app or **refresh** the secret:

```bash
cd /opt/baytemps
SECRET_ID=your-secret-name AWS_REGION=us-east-1 ./ec2-start-baytemps.sh
```

That will recreate the env file from the current secret and recreate the container. You can also add a systemd service (see the main README) so this runs automatically at boot if you prefer.
