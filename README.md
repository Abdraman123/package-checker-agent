# Package Version Checker A2A Agent

An intelligent AI agent that checks package versions from PyPI (Python) and npm (JavaScript/Node.js) registries. Built with FastAPI and compliant with the A2A (Agent-to-Agent) protocol for seamless integration with Telex.im.

## 🚀 Features

- ✅ Check Python packages from PyPI
- ✅ Check JavaScript/Node.js packages from npm
- ✅ Natural language query support
- ✅ A2A protocol compliant (JSON-RPC 2.0)
- ✅ No API keys required (uses public APIs)
- ✅ Fast and lightweight
- ✅ Easy deployment to DigitalOcean

## 📋 Prerequisites

- Python 3.11+
- pip (Python package manager)
- Git

## 🛠️ Local Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/package-checker-agent.git
cd package-checker-agent
```

### 2. Create Project Structure

```bash
mkdir -p models agents
```

### 3. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -e .
```

### 5. Set Up Environment Variables

Create a `.env` file:

```bash
PORT=8080
```

### 6. Run the Server

```bash
python main.py
```

The server will start at `http://localhost:8080`

## 🧪 Testing Locally

### Test Health Endpoint

```bash
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "healthy",
  "agent": "package-checker",
  "version": "1.0.0"
}
```

### Test A2A Endpoint with PyPI Package

```bash
curl -X POST http://localhost:8080/a2a/package \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-001",
    "method": "message/send",
    "params": {
      "message": {
        "kind": "message",
        "role": "user",
        "parts": [
          {
            "kind": "text",
            "text": "Check fastapi"
          }
        ],
        "messageId": "msg-001"
      }
    }
  }'
```

### Test with npm Package

```bash
curl -X POST http://localhost:8080/a2a/package \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "test-002",
    "method": "message/send",
    "params": {
      "message": {
        "kind": "message",
        "role": "user",
        "parts": [
          {
            "kind": "text",
            "text": "npm package react"
          }
        ],
        "messageId": "msg-002"
      }
    }
  }'
```

## 🌐 Deployment to DigitalOcean

### Method 1: DigitalOcean App Platform (Recommended)

1. **Push your code to GitHub**

```bash
git init
git add .
git commit -m "Initial commit: Package Checker Agent"
git branch -M main
git remote add origin https://github.com/yourusername/package-checker-agent.git
git push -u origin main
```

2. **Create App on DigitalOcean**

- Go to [DigitalOcean App Platform](https://cloud.digitalocean.com/apps)
- Click "Create App"
- Select "GitHub" as source
- Authorize DigitalOcean to access your repository
- Choose your repository and branch (`main`)

3. **Configure the App**

```
Name: package-checker-agent
Region: Choose closest to you (e.g., New York)
Build Command: pip install -e .
Run Command: python main.py
HTTP Port: 8080
Instance Size: Basic (512 MB RAM, $5/month)
```

4. **Set Environment Variables**

In the DigitalOcean dashboard, go to Settings → Environment Variables:

```
PORT = 8080
```

5. **Deploy**

- Click "Next" → "Create Resources"
- Wait 3-5 minutes for deployment
- You'll get a URL like: `https://package-checker-agent-xxxxx.ondigitalocean.app`

6. **Verify Deployment**

```bash
curl https://your-app.ondigitalocean.app/health
```

### Method 2: DigitalOcean Droplet

1. **Create Ubuntu Droplet**

- Size: Basic (1 GB RAM, $6/month)
- OS: Ubuntu 22.04 LTS
- Add SSH key

2. **SSH into Droplet**

```bash
ssh root@your-droplet-ip
```

3. **Install Dependencies**

```bash
apt update
apt install python3-pip python3-venv git -y
```

4. **Clone Repository**

```bash
git clone https://github.com/yourusername/package-checker-agent.git
cd package-checker-agent
```

5. **Set Up Virtual Environment**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

6. **Create Systemd Service**

Create `/etc/systemd/system/package-agent.service`:

```ini
[Unit]
Description=Package Checker A2A Agent
After=network.target

[Service]
User=root
WorkingDirectory=/root/package-checker-agent
Environment="PATH=/root/package-checker-agent/venv/bin"
ExecStart=/root/package-checker-agent/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

7. **Start Service**

```bash
systemctl enable package-agent
systemctl start package-agent
systemctl status package-agent
```

8. **Configure Firewall**

```bash
ufw allow 8080
ufw enable
```

## 🔗 Telex Integration

### 1. Get Telex Access

Run this command in HNG Slack:

```
/telex-invite your-email@example.com
```

### 2. Update workflow.json

Edit `workflow.json` and replace the URL with your deployed endpoint:

```json
{
  "nodes": [
    {
      "url": "https://your-app.ondigitalocean.app/a2a/package"
    }
  ]
}
```

### 3. Submit to Telex

Follow the instructions provided by HNG mentors to submit your `workflow.json` to Telex.

### 4. Test in Telex

Once integrated, you can chat with your agent:

```
You: Check fastapi
Agent: 📦 fastapi (from PyPI)
       Version: 0.115.0
       Description: FastAPI framework, high performance...
       Install: pip install fastapi

You: npm package express
Agent: 📦 express (from npm)
       Version: 4.19.2
       Description: Fast, unopinionated, minimalist...
       Install: npm install express
```

## 📖 API Documentation

### Endpoints

#### `GET /`
Root endpoint with API information

#### `GET /health`
Health check endpoint

#### `POST /a2a/package`
Main A2A endpoint for package checking

### Supported Query Formats

- `Check [package-name]`
- `Latest version of [package-name]`
- `npm package [package-name]`
- `python package [package-name]`
- `pip [package-name]`
- `[package-name]`

### Example Queries

- "Check fastapi"
- "Latest version of react"
- "npm express"
- "python django"
- "Info about tensorflow"

## 🏗️ Project Structure

```
package-checker-agent/
├── main.py              # FastAPI app and API endpoints
├── models.py            # Pydantic schemas for A2A protocol
├── services.py          # Business logic for package checking
├── database.py          # Database/caching placeholder (future use)
├── config.py            # Application settings and environment variables
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (not in git)
├── .gitignore          # Git ignore rules
├── Dockerfile          # Docker configuration
├── workflow.json       # Telex integration config
└── README.md           # Project documentation (this file)
```

## 🔧 Development

### Adding New Features

The agent is modular and easy to extend:

1. **Add new package registries** in `agents/package_agent.py`
2. **Modify response format** in `_format_response()` method
3. **Add caching** for faster responses
4. **Add rate limiting** for production use

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find process using port 8080
lsof -i :8080

# Kill the process
kill -9 <PID>
```

### Package Not Found

Make sure the package name is spelled correctly. The agent checks both PyPI and npm automatically.

### Deployment Issues on DigitalOcean

- Check logs in DigitalOcean dashboard
- Verify environment variables are set
- Ensure PORT is 8080
- Check if the build command completed successfully

## 📝 License

MIT License

## 👤 Author

Built for HNG Internship Stage 3

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- PyPI and npm for their public APIs
- Telex.im for the A2A protocol
- HNG Internship for the opportunity

## 📞 Support

For issues or questions:
- Open an issue on GitHub
- Ask in HNG Slack channel
- Check Telex documentation

---

**Happy Coding! 🚀**