from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
import subprocess
import tempfile
import base64
import os
import json

router = APIRouter(tags=["Debug"])

ADMIN_KEY = os.getenv("ADMIN_KEY")
COOKIE_FILE_PATH = None

def load_cookie_file():
    """Load cookies from base64 env var and save to temp file"""
    global COOKIE_FILE_PATH
    cookies_b64 = os.getenv("YTDLP_COOKIES_B64")
    
    if not cookies_b64:
        COOKIE_FILE_PATH = None
        return None
    
    try:
        if COOKIE_FILE_PATH and os.path.exists(COOKIE_FILE_PATH):
            try:
                os.unlink(COOKIE_FILE_PATH)
            except:
                pass
        
        cookie_data = base64.b64decode(cookies_b64)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".txt", mode="wb")
        temp_file.write(cookie_data)
        temp_file.close()
        COOKIE_FILE_PATH = temp_file.name
        return COOKIE_FILE_PATH
    except Exception as e:
        print(f"Cookie decode failed: {e}")
        COOKIE_FILE_PATH = None
        return None

def get_cookie_status():
    """Get current cookie file status"""
    if COOKIE_FILE_PATH and os.path.exists(COOKIE_FILE_PATH):
        try:
            size = os.path.getsize(COOKIE_FILE_PATH)
            with open(COOKIE_FILE_PATH, 'r') as f:
                lines = len(f.readlines())
            return f"Loaded ({size} bytes, {lines} lines)"
        except Exception as e:
            return f"Error: {e}"
    elif os.getenv("YTDLP_COOKIES_B64"):
        return "Not loaded (run 'loadcookies')"
    else:
        return "Not configured"

@router.get("/debug/formats")
def list_formats(url: str = Query(...), key: str = Query(...)):
    if key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid key")
    
    cookie_file = COOKIE_FILE_PATH if (COOKIE_FILE_PATH and os.path.exists(COOKIE_FILE_PATH)) else load_cookie_file()
    
    try:
        command = ["yt-dlp", "--list-formats", url]
        if cookie_file:
            command.extend(["--cookies", cookie_file])
        
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        return {
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    finally:
        pass


# ============== SHELL TERMINAL ==============

@router.get("/debug/shell", response_class=HTMLResponse)
def shell_terminal_page(key: str = Query(...)):
    if key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid key")
    
    html_content = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>GL$TCH-SPI Shell</title>
    <style>
        body { background: #0d1117; color: #c9d1d9; font-family: monospace; margin: 0; padding: 20px; }
        h1 { color: #58a6ff; }
        .container { max-width: 1200px; margin: 0 auto; }
        .info-bar { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 10px 15px; margin-bottom: 15px; display: flex; gap: 20px; }
        .info-item label { color: #8b949e; font-size: 12px; }
        .info-item span { color: #7ee787; }
        .terminal { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; }
        .output { background: #0d1117; border: 1px solid #30363d; border-radius: 4px; padding: 15px; min-height: 400px; max-height: 500px; overflow-y: auto; white-space: pre-wrap; font-size: 14px; }
        .stdout { color: #7ee787; }
        .stderr { color: #ffa657; }
        .command { color: #58a6ff; font-weight: bold; }
        .error { color: #f85149; }
        .prompt { color: #8b949e; }
        .input-group { display: flex; gap: 10px; margin-top: 15px; }
        input { flex: 1; background: #0d1117; border: 1px solid #30363d; color: #c9d1d9; padding: 12px; border-radius: 4px; font-family: monospace; }
        button { background: #238636; color: white; border: none; padding: 12px 24px; border-radius: 4px; cursor: pointer; }
        button:hover { background: #2ea043; }
        button:disabled { background: #484f58; cursor: not-allowed; }
        .controls { margin: 15px 0; }
        .controls button { background: #1f6feb; margin-right: 10px; padding: 8px 16px; font-size: 12px; }
        .controls button.clear { background: #da3633; }
        .controls button.cookie { background: #8957e5; }
        .status { margin-top: 10px; padding: 10px; border-radius: 4px; display: none; background: rgba(88, 166, 255, 0.1); border: 1px solid #58a6ff; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🖥️ GL$TCH-SPI Shell Terminal</h1>
        
        <div class="info-bar">
            <div class="info-item">
                <label>Cookies:</label>
                <span id="cookieStatus">Checking...</span>
            </div>
            <div class="info-item">
                <label>Dir:</label>
                <span>''' + os.getcwd() + '''</span>
            </div>
        </div>
        
        <div class="controls">
            <button onclick="run('ls -la')">ls -la</button>
            <button onclick="run('pwd')">pwd</button>
            <button onclick="run('ps aux')">ps aux</button>
            <button onclick="run('df -h')">df -h</button>
            <button onclick="run('free -m')">free -m</button>
            <button class="cookie" onclick="run('loadcookies')">🍪 Load Cookies</button>
            <button class="cookie" onclick="run('cookiestatus')">🍪 Status</button>
            <button class="cookie" onclick="run('rmcookie')">🗑️ Remove</button>
            <button class="clear" onclick="clearTerm()">Clear</button>
        </div>
        
        <div class="terminal">
            <div id="output" class="output">
                <span class="prompt">$ Welcome to GL$TCH-SPI Shell</span>
                <span class="prompt">$ Admin key validated.</span>
            </div>
            
            <div class="input-group">
                <input type="text" id="cmdInput" placeholder="Enter command..." onkeypress="if(event.key==='Enter')execute()" autofocus>
                <button onclick="execute()" id="runBtn">Run</button>
            </div>
            
            <div id="status" class="status">⏳ Running...</div>
        </div>
    </div>

    <script>
        const KEY = "''' + key + '''";
        const output = document.getElementById('output');
        const cmdInput = document.getElementById('cmdInput');
        const runBtn = document.getElementById('runBtn');
        const status = document.getElementById('status');
        const cookieStatus = document.getElementById('cookieStatus');

        fetch('/debug/shell/cookiestatus?key=' + KEY)
            .then(r => r.json())
            .then(d => cookieStatus.textContent = d.status)
            .catch(() => cookieStatus.textContent = 'Error');

        function run(cmd) {
            cmdInput.value = cmd;
            execute();
        }

        function clearTerm() {
            output.innerHTML = '<span class="prompt">$ Cleared</span>';
        }

        function append(cmd, out, err, code) {
            const div = document.createElement('div');
            div.innerHTML = '<div class="command">$ ' + cmd + '</div>' +
                (out ? '<div class="stdout">' + out + '</div>' : '') +
                (err ? '<div class="stderr">' + err + '</div>' : '') +
                (code !== 0 ? '<div class="error">Exit: ' + code + '</div>' : '');
            output.appendChild(div);
            output.scrollTop = output.scrollHeight;
        }

        async function execute() {
            const cmd = cmdInput.value.trim();
            if (!cmd) return;
            
            runBtn.disabled = true;
            status.style.display = 'block';
            
            try {
                const res = await fetch('/debug/shell/execute?key=' + KEY, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({command: cmd})
                });
                const data = await res.json();
                if (res.ok) {
                    append(cmd, data.stdout, data.stderr, data.returncode);
                    if (['loadcookies','cookiestatus','rmcookie'].includes(cmd.split(' ')[0])) {
                        cookieStatus.textContent = data.cookie_status || 'Updated';
                    }
                } else {
                    append(cmd, '', data.detail, 1);
                }
            } catch (e) {
                append(cmd, '', 'Error: ' + e.message, 1);
            }
            
            cmdInput.value = '';
            runBtn.disabled = false;
            status.style.display = 'none';
            cmdInput.focus();
        }
    </script>
</body>
</html>
    '''
    return html_content


@router.post("/debug/shell/execute")
def execute_shell_command(request: Request, key: str = Query(...)):
    global COOKIE_FILE_PATH
    
    if key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid key")
    
    body = request.json()
    command = body.get("command", "").strip()
    
    if not command:
        raise HTTPException(status_code=400, detail="No command")
    
    # Built-in commands
    if command == "loadcookies":
        path = load_cookie_file()
        return {
            "stdout": f"Loaded: {path}" if path else "Failed (YTDLP_COOKIES_B64 not set?)",
            "stderr": "",
            "returncode": 0 if path else 1,
            "cookie_status": get_cookie_status()
        }
    
    if command == "cookiestatus":
        return {
            "stdout": get_cookie_status(),
            "stderr": "",
            "returncode": 0,
            "cookie_status": get_cookie_status()
        }
    
    if command == "rmcookie":
        if COOKIE_FILE_PATH and os.path.exists(COOKIE_FILE_PATH):
            os.unlink(COOKIE_FILE_PATH)
            COOKIE_FILE_PATH = None
        return {
            "stdout": "Cookie file deleted",
            "stderr": "",
            "returncode": 0,
            "cookie_status": get_cookie_status()
        }
    
    # Block dangerous commands
    blocked = ["rm -rf /", "rm -rf /*", ":(){", "while true", "fork", "shutdown", "reboot", "mkfs"]
    for block in blocked:
        if block in command.lower():
            raise HTTPException(status_code=403, detail=f"Blocked: {block}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, cwd=os.getcwd())
        
        # Filter env output
        stdout = result.stdout
        if command.strip() in ["env", "printenv"]:
            lines = stdout.split('\n')
            filtered = [l for l in lines if not any(x in l.lower() for x in ['admin_key', 'password', 'secret', 'token', 'cookie'])]
            stdout = '\n'.join(filtered)
        
        return {
            "stdout": stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Timeout")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/shell/cookiestatus")
def cookie_status(key: str = Query(...)):
    if key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid key")
    
    return {
        "status": get_cookie_status(),
        "loaded": COOKIE_FILE_PATH is not None and os.path.exists(COOKIE_FILE_PATH) if COOKIE_FILE_PATH else False
    }
