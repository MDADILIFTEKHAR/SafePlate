# SafePlate — Troubleshooting & Operations Guide 🛠️

This document provides quick diagnostics and solutions for common operational and environment issues.

---

## 1. Ollama Issues

### Problem: "Ollama Offline" or `ConnectionRefusedError`
- **Symptom**: The navbar displays `Ollama Offline` or generation attempts time out.
- **Cause**: The Ollama background service is not running on `http://localhost:11434`.
- **Solution 1**: Start Ollama:
  ```bash
  # Windows / macOS / Linux:
  ollama serve
  ```
- **Solution 2**: Use Demo Mode (No Ollama Required):
  In your `.env` file, set:
  ```env
  DEMO_MODE=true
  ```
  Restart the backend server. SafePlate will immediately use the high-fidelity deterministic provider, executing the full validation pipeline without requiring Ollama.

### Problem: "Model not found" or slow generation
- **Symptom**: Ollama returns HTTP 404 or hangs trying to load an uninstalled model.
- **Solution**: Pull the configured model explicitly:
  ```bash
  ollama pull llama3.2:3b
  ```
  Check existing models:
  ```bash
  ollama list
  ```

---

## 2. Port Conflicts (Port 8000 or 5173 in use)

### Problem: `Address already in use` (Port 8000)
- **Windows PowerShell**:
  ```powershell
  Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force
  ```
- **macOS / Linux**:
  ```bash
  lsof -ti:8000 | xargs kill -9
  ```
- **Alternative**: Change the backend port in `.env`:
  ```env
  PORT=8001
  ```
  And update the proxy target in `frontend/vite.config.js`.

### Problem: Port 5173 in use
- Vite will automatically attempt to bind to `5174` or `5175`.
- Ensure the backend `CORS_ORIGINS` in `.env` includes the new port if running on a custom port.

---

## 3. Database Initialization & Reset

### Problem: `Database locked` or malformed schema
SafePlate uses SQLite (`safeplate.db`). Database migrations and initialization are strictly idempotent.
- **To reset database to clean state**:
  ```bash
  # Windows PowerShell:
  Remove-Item -Force safeplate.db
  $env:PYTHONPATH='backend'
  .\.venv\Scripts\python -c "from app.database.init_db import init_db; init_db()"

  # macOS / Linux:
  rm -f safeplate.db
  PYTHONPATH=backend .venv/bin/python -c "from app.database.init_db import init_db; init_db()"
  ```

---

## 4. Frontend Connection & CORS Issues

### Problem: `Network error: Unable to reach SafePlate server`
- **Cause**: Backend is not running or proxy is misconfigured.
- **Diagnostics**:
  1. Open [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health) directly in your browser.
  2. If the health JSON appears, check that `frontend/vite.config.js` has the proxy enabled:
     ```javascript
     proxy: {
       '/api': {
         target: 'http://127.0.0.1:8000',
         changeOrigin: true,
       }
     }
     ```
  3. Ensure both servers are running simultaneously.

---

## 5. Python Environment & Dependency Issues

### Problem: `ModuleNotFoundError: No module named 'app'`
- **Cause**: Python path is not configured to include `backend/`.
- **Solution**:
  - Windows: `$env:PYTHONPATH='backend'`
  - macOS/Linux: `export PYTHONPATH=backend`

### Problem: Starlette or Pydantic Version Conflicts
- Run a clean reinstall inside `.venv`:
  ```bash
  .\.venv\Scripts\pip install --upgrade pip
  .\.venv\Scripts\pip install -r backend/requirements.txt
  ```

---

## 6. Running Tests

If tests fail due to environment variables:
```bash
# Windows PowerShell:
$env:PYTHONPATH='backend'
$env:DEMO_MODE='true'
.\.venv\Scripts\pytest backend/tests -v

# Frontend tests:
cd frontend
npm run test
```
