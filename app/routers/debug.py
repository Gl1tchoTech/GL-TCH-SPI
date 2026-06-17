from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import HTMLResponse
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
        # Clean up old file if exists
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
        return "Not configured (YTDLP_COOKIES_B64 not set)"


@router.get("/debug/formats")
def list_formats(url: str = Query(...), key: str = Query(...)):
    """List available formats for a YouTube URL"""
    if key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid key")
    
    # Ensure cookie file is loaded
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== SHELL TERMINAL ==============

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>GL$TCH-SPI Shell</title>
    <style>
        body { background: #0d1117; color: #c9d1d9; font-family: 'Courier New', monospace; margin: 0; padding: 20px; min-height: 100vh; }
        h1 { color: #58a6ff; margin-bottom: 10px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .info-bar { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 10px 15px; margin-bottom: 15px; display: flex; gap: 20px; flex-wrap: wrap; }
        .info-item { display: flex; align-items: center; gap: 8px; }
        .info-item label { color: #8b949e; font-size: 12px; }
        .info-item span { color: #7ee787; font-weight: bold; }
        .info-item span.error { color: #f85149; }
        .terminal { background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 15px; }
        .output { background: #0d1117; border: 1px solid #30363d; border-radius: 4px; padding: 15px; min-height: 400px; max-height: 500px; overflow-y: auto; white-space: pre-wrap; word-wrap: break-word; font-size: 14px; line-height: 1.5; }
        .stdout { color: #7ee787; }
        .stderr { color: #ffa657; }
        .command { color: #58a6ff; font-weight: bold; }
        .error { color: #f85149; }
        .prompt { color: #8b949e; }
        .info { color: #a371f7; }
        .input-group { display: flex; gap: 10px; margin-top: 15px; }
        input[type="text"] { flex: 1; background: #0d1117; border: 1px solid #30363d; color: #c9d1d9; padding: 12px; border-radius: 4px; font-family: inherit; font-size: 14px; }
        button { background: #238636; color: white; border: none; padding: 12px 24px; border-radius: 4px; cursor: pointer; font-size: 14px; }
        button:hover { background: #2ea043; }
        button:disabled { background: #484f58; cursor: not-allowed; }
        .controls { margin: 15px 0; }
        .controls button { background: #1f6feb; margin-right: 10px; padding: 8px 16px; font-size: 12px; }
        .controls button.clear { background: #da3633; }
        .controls button.cookie { background: #8957e5; }
        .status { margin-top: 10px; padding: 10px; border-radius: 4px; display: none; background: rgba(88, 166, 255, 0.1); border: 1px solid #58a6ff; }
        .section { margin-top: 10px; padding: 10px; background: #0d1117; border-radius: 4px; font-size: 12px; }
        .section h3 { margin: 0 0 10px 0; color: #58a6ff; font-size: 13px; }
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
                <label>Working Dir:</label>
                <span>{cwd}</span>
            </div>
        </div>
        
        <div class="controls">
            <button onclick="runCmd('ls -la')">ls -la</button>
            <button onclick="runCmd('pwd')">pwd</button>
            <button onclick="runCmd('ps aux')">ps aux</button>
            <button onclick="runCmd('df -h')">df -h</button>
            <button onclick="runCmd('free -m')">free -m</button>
            <button onclick="runCmd('env')">env</button>
            <button class="cookie" onclick="runCmd('loadcookies')">🍪 Load Cookies</button>
            <button class="cookie" onclick="runCmd('cookiestatus')">🍪 Status</button>
            <button class="cookie" onclick="runCmd('rmcookie')">🗑️ Remove</button>
            <button class="clear" onclick="clearTerm()">Clear</button>
        </div>
        
        <div class="section">
            <h3>Built-in Commands:</h3>
            <code>loadcookies</code> - Load YTDLP_COOKIES_B64 from env &nbsp;|&nbsp;
            <code>cookiestatus</code> - Show cookie file status &nbsp;|&nbsp;
            <code>rmcookie</code> - Delete temp cookie file
        </div>
        
        <div class="terminal">
            <div id="output" class="output">
                <span class="prompt">$ Welcome to GL$TCH-SPI Shell</span>
                <span class="prompt">$ Admin key validated. Ready for commands.</span>
            </div>
            
            <div class="input-group">
                <input type="text" id="cmdInput" placeholder="Enter command..." onkeypress="if(event.key==='Enter')execute()" autofocus>
                <button onclick="execute()" id="runBtn">Run</button>
            </div>
            
            <div id="status" class="status">⏳ Executing...</div>
        </div>
    </div>

    <script>
        const ADMIN_KEY = "{key}";
        const output = document.getElementById('output');
        const cmdInput = document.getElementById('cmdInput');
        const runBtn = document.getElementById('runBtn');
        const status = document.getElementById('status');
        const cookieStatus = document.getElementById('cookieStatus');

        // Check cookie status on load
        fetch('/debug/shell/cookiestatus?key=' + ADMIN_KEY)
            .then(r => r.json())
            .then(d => {{
                cookieStatus.textContent = d.status;
                cookieStatus.className = d.loaded ? '' : 'error';
            }})
            .catch(() => {{
                cookieStatus.textContent = 'Error checking';
                cookieStatus.className = 'error';
            }});

        function runCmd(cmd) {{
            cmdInput.value = cmd;
            execute();
        }}

        function clearTerm() {{
            output.innerHTML = '<span class="prompt">$ Terminal cleared</span><span class="prompt">$</span>';
        }}

        function appendOutput(command, stdout, stderr, returncode, isInfo) {{
            const div = document.createElement('div');
            if (isInfo) {{
                div.innerHTML = '<div class="info">ℹ️ ' + escapeHtml(stdout) + '</div>';
            }} else {{
                div.innerHTML = '<div class="command">$ ' + escapeHtml(command) + '</div>' +
                    (stdout ? '<div class="stdout">' + escapeHtml(stdout) + '</div>' : '') +
                    (stderr ? '<div class="stderr">' + escapeHtml(stderr) + '</div>' : '') +
                    (returncode !== 0 ? '<div class="error">Exit code: ' + returncode + '</div>' : '');
            }}
            output.appendChild(div);
            output.scrollTop = output.scrollHeight;
        }}

        function escapeHtml(text) {{
            if (!text) return '';
            return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
        }}

        async function execute() {{
            const command = cmdInput.value.trim();
            if (!command) return;

            runBtn.disabled = true;
            status.style.display = 'block';

            try {{
                const response = await fetch('/debug/shell/execute?key=' + ADMIN_KEY, {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ command: command }})
                }});

                const data = await response.json();
                
                if (response.ok) {{
                    appendOutput(command, data.stdout, data.stderr, data.returncode, data.is_info);
                    // Update cookie status display
                    if (['loadcookies','cookiestatus','rmcookie'].includes(command.split(' ')[0])) {{
                        cookieStatus.textContent = data.cookie_status || 'Updated';
                        cookieStatus.className = (data.cookie_status && data.cookie_status.includes('Loaded')) ? '' : 'error';
                    }}
                }} else {{
                    appendOutput(command, '', data.detail || 'Error', 1, false);
                }}
            }} catch (error) {{
                appendOutput(command, '', 'Network error: ' + error.message, 1, false);
            }}

            cmdInput.value = '';
            runBtn.disabled = false;
            status.style.display = 'none';
            cmdInput.focus();
        }}
    </script>
</body>
</html>"""


@router.get("/debug/shell", response_class=HTMLResponse)
def shell_terminal_page(key: str = Query(...)):
    """Serve the web terminal page - requires admin key in URL"""
    if key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid key")
    
    return HTML_TEMPLATE.format(cwd=os.getcwd(), key=key)


@router.post("/debug/shell/execute")
async def execute_shell_command(request: Request, key: str = Query(...)):
    """Execute a shell command - requires admin key"""
    global COOKIE_FILE_PATH
    
    if key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid key")
    
    try:
        body = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid JSON body")
    
    command = body.get("command", "").strip()
    
    if not command:
        raise HTTPException(status_code=400, detail="No command provided")
    
    # Handle built-in cookie commands
    if command == "loadcookies":
        path = load_cookie_file()
        status = get_cookie_status()
        return {
            "stdout": f"Cookies loaded: {path}" if path else "Failed - YTDLP_COOKIES_B64 not set or invalid",
            "stderr": "",
            "returncode": 0 if path else 1,
            "is_info": True,
            "cookie_status": status
        }
    
    if command == "cookiestatus":
        status = get_cookie_status()
        return {
            "stdout": status,
            "stderr": "",
            "returncode": 0,
            "is_info": True,
            "cookie_status": status
        }
    
    if command == "rmcookie":
        if COOKIE_FILE_PATH and os.path.exists(COOKIE_FILE_PATH):
            try:
                os.unlink(COOKIE_FILE_PATH)
            except Exception as e:
                return {"stdout": "", "stderr": str(e), "returncode": 1}
        COOKIE_FILE_PATH = None
        status = get_cookie_status()
        return {
            "stdout": "Cookie file deleted",
            "stderr": "",
            "returncode": 0,
            "is_info": True,
            "cookie_status": status
        }
    
    # Security: Block dangerous commands
    blocked = ["rm -rf /", "rm -rf /*", ":(){", "while true", "fork", "shutdown", "reboot", "mkfs", "dd if=/dev/zero", "> /dev/sda"]
    cmd_lower = command.lower()
    for block in blocked:
        if block in cmd_lower:
            raise HTTPException(status_code=403, detail=f"Command blocked for security: {block}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd()
        )
        
        # Filter env output to hide sensitive vars
        stdout = result.stdout
        if command.strip() in ["env", "printenv"]:
            lines = stdout.split('\n')
            filtered = []
            for line in lines:
                lower = line.lower()
                if not any(s in lower for s in ['admin_key', 'password', 'secret', 'token', 'cookie', 'api_key', 'private']):
                    filtered.append(line)
            stdout = '\n'.join(filtered)
        
        return {
            "stdout": stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "is_info": False
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Command timed out after 30 seconds")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/shell/cookiestatus")
def cookie_status(key: str = Query(...)):
    """Get current cookie file status"""
    if key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Invalid key")
    
    is_loaded = COOKIE_FILE_PATH is not None and os.path.exists(COOKIE_FILE_PATH) if COOKIE_FILE_PATH else False
    return {
        "status": get_cookie_status(),
        "loaded": is_loaded,
        "path": COOKIE_FILE_PATH
    }
