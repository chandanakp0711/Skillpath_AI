# ☁️ Deployment Guide — SkillPath AI

This app is a standard Streamlit application, so it deploys anywhere Python runs. Below are complete, copy-paste guides for **Streamlit Community Cloud**, **AWS EC2** and **Google Cloud**.

> **Pre-flight checklist (all targets)**
> - `requirements.txt` is present and current ✅
> - `models/` artefacts are committed **or** `train.py` runs at build time
> - App entry point is `app.py`; default port is `8501`
> - `.streamlit/config.toml` provides the theme (secrets go in `.streamlit/secrets.toml`, which is git-ignored)

---

## 1. Streamlit Community Cloud (easiest — free)

1. Push the project to a **public GitHub repository**.
   ```bash
   git init && git add . && git commit -m "SkillPath AI"
   git branch -M main
   git remote add origin https://github.com/<you>/skillpath-ai.git
   git push -u origin main
   ```
2. Go to **https://share.streamlit.io** → *New app*.
3. Select your repo/branch, set **Main file path** = `app.py`.
4. (Optional) *Advanced settings* → Python version `3.11`.
5. Click **Deploy**. Streamlit installs `requirements.txt` and serves the app at `https://<app-name>.streamlit.app`.

> The committed `models/*.pkl` make the app start instantly. If you exclude them, add a one-time build step or call `train.py` lazily on first run.

---

## 2. AWS EC2 (full control)

### 2.1 Launch & connect
1. Launch an **Ubuntu 22.04** instance (t3.small or larger).
2. **Security Group:** allow SSH (22) from your IP and a custom TCP rule for **8501** (or 80 if using Nginx).
3. SSH in:
   ```bash
   ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>
   ```

### 2.2 Install & run
```bash
sudo apt update && sudo apt install -y python3-pip python3-venv git
git clone https://github.com/<you>/skillpath-ai.git && cd skillpath-ai
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python train.py          # generate model artefacts (if not committed)

# quick test
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```
Visit `http://<EC2_PUBLIC_IP>:8501`.

### 2.3 Run as a service (survives reboots)
```bash
sudo tee /etc/systemd/system/skillpath.service > /dev/null <<'EOF'
[Unit]
Description=SkillPath AI Streamlit App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/skillpath-ai
ExecStart=/home/ubuntu/skillpath-ai/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now skillpath
sudo systemctl status skillpath
```

### 2.4 (Optional) Nginx reverse proxy on port 80
```bash
sudo apt install -y nginx
sudo tee /etc/nginx/sites-available/skillpath > /dev/null <<'EOF'
server {
    listen 80;
    server_name _;
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 86400;
    }
}
EOF
sudo ln -s /etc/nginx/sites-available/skillpath /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl restart nginx
```
Now the app is at `http://<EC2_PUBLIC_IP>/`. Add HTTPS with `certbot` if you have a domain.

---

## 3. Google Cloud

### Option A — Cloud Run (serverless, recommended)
1. Add a **`Dockerfile`** (see §4) to the repo.
2. Build & deploy:
   ```bash
   gcloud auth login
   gcloud config set project <PROJECT_ID>
   gcloud builds submit --tag gcr.io/<PROJECT_ID>/skillpath
   gcloud run deploy skillpath \
     --image gcr.io/<PROJECT_ID>/skillpath \
     --platform managed --region asia-south1 \
     --allow-unauthenticated --port 8501 --memory 1Gi
   ```
3. Cloud Run returns a public HTTPS URL.

### Option B — App Engine (flexible)
Create `app.yaml`:
```yaml
runtime: python311
entrypoint: streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
instance_class: F2
```
Deploy: `gcloud app deploy`.

### Option C — Compute Engine VM
Identical to the AWS EC2 steps (§2) — create a VM, open the firewall for 8501, install, and run via `systemd`.

---

## 4. Dockerfile (for Cloud Run / any container host)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Train at build time if models are not committed:
RUN python train.py || true

EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1
ENTRYPOINT ["streamlit", "run", "app.py", \
            "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
```

Build & run locally:
```bash
docker build -t skillpath .
docker run -p 8501:8501 skillpath
```

---

## 5. Troubleshooting

| Symptom | Fix |
|---|---|
| `Model artefacts not found` | Run `python train.py`, or commit `models/*.pkl`. The app uses a rule-based fallback meanwhile. |
| Blank page / connection refused | Ensure `--server.address 0.0.0.0` and the firewall/security-group allows the port. |
| WebSocket disconnects behind proxy | Add the `Upgrade`/`Connection` headers (see Nginx config) and a long `proxy_read_timeout`. |
| `xgboost` install fails | It's optional — remove it from `requirements.txt`; the app runs on the other 4 models. |
| Out-of-memory on small instances | Use ≥1 GB RAM; Random Forest with 400 trees loads comfortably under that. |
