from flask import Flask, request, jsonify
import subprocess, tempfile, os

app = Flask(__name__)

@app.route('/run', methods=['POST'])
def run():
    code = request.json.get('code', '')
    with tempfile.NamedTemporaryFile(mode='w', suffix='.slacker', delete=False) as f:
        f.write(code)
        path = f.name
    try:
        r = subprocess.run(
            ['python3', os.path.join(os.path.dirname(__file__), 'group-project.py'), path],
            capture_output=True, text=True, timeout=5
        )
        return jsonify({'output': r.stdout, 'error': r.stderr})
    except subprocess.TimeoutExpired:
        return jsonify({'output': '', 'error': 'timeout'})
    finally:
        os.unlink(path)

@app.route('/')
def index():
    return '''
<!DOCTYPE html>
<html>
<head>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  background: #0d1117;
  color: #c9d1d9;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 20px;
}
h1 {
  font-size: 1.4rem;
  color: #58a6ff;
  margin-bottom: 4px;
}
.subtitle {
  color: #8b949e;
  font-size: 0.8rem;
  margin-bottom: 24px;
}
.container {
  width: 100%;
  max-width: 720px;
}
textarea {
  width: 100%;
  height: 320px;
  background: #161b22;
  color: #c9d1d9;
  border: 1px solid #30363d;
  border-radius: 6px;
  padding: 16px;
  font-family: inherit;
  font-size: 0.85rem;
  line-height: 1.6;
  resize: vertical;
  outline: none;
}
textarea:focus {
  border-color: #58a6ff;
}
.toolbar {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}
button {
  background: #238636;
  color: #fff;
  border: none;
  border-radius: 6px;
  padding: 10px 24px;
  font-family: inherit;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.15s;
}
button:hover { background: #2ea043; }
button:active { background: #1a6327; }
.reset {
  background: #21262d;
  border: 1px solid #30363d;
}
.reset:hover { background: #30363d; }
#out {
  margin-top: 16px;
  background: #161b22;
  border: 1px solid #30363d;
  border-radius: 6px;
  padding: 16px;
  font-size: 0.85rem;
  line-height: 1.6;
  white-space: pre-wrap;
  min-height: 60px;
  color: #7ee787;
}
#out.error { color: #f85149; }
.badge {
  display: inline-block;
  background: #1f6feb33;
  color: #58a6ff;
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 0.7rem;
  margin-top: 16px;
}
</style>
</head>
<body>
<h1>Group Project</h1>
<p class="subtitle">A joke esolang where programs are group chats</p>
<div class="container">
  <textarea id="code">@me: ok so the prof said we need to count to 5
@slacker: ok
@me: x is 0
@deadline: due in 5
@slacker: when is it due
@me: print x
@me: x is x + 1
@slacker: cool
@me: print x
@me: x is x + 1
@parent: are you guys done yet
@me: no
@me: print x
@me: x is x + 1
@deadline: done
@slacker: I'll send it later
@me: phew
@prof: here's our answer: x</textarea>
  <div class="toolbar">
    <button onclick="go()">Run</button>
    <button class="reset" onclick="reset()">Reset</button>
  </div>
  <pre id="out"></pre>
  <span class="badge">python 3.6+ · no dependencies · .slacker</span>
</div>
<script>
const DEFAULT = document.getElementById('code').value;
async function go() {
  const out = document.getElementById('out');
  out.className = '';
  out.textContent = 'running...';
  const r = await fetch('/run', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({code: document.getElementById('code').value})
  });
  const d = await r.json();
  out.textContent = d.output || d.error || '(no output)';
  if (d.error && !d.output) out.className = 'error';
}
function reset() {
  document.getElementById('code').value = DEFAULT;
  document.getElementById('out').textContent = '';
}
</script>
</body>
</html>'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))   
