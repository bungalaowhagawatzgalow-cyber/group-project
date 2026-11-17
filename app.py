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
    <html>
    <body style="font-family:monospace;background:#1a1a1a;color:#eee;padding:20px;">
      <h2>Group Project</h2>
      <textarea id="code" rows="20" cols="70" style="background:#222;color:#eee;border:1px solid #444;padding:10px;width:100%;box-sizing:border-box;">@me: ok so the prof said we need to count to 5
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
      <br><button onclick="go()" style="padding:8px 16px;margin-top:8px;">Run</button>
      <pre id="out" style="background:#111;padding:10px;margin-top:10px;white-space:pre-wrap;"></pre>
      <script>
      async function go() {
        document.getElementById('out').textContent = '...';
        const r = await fetch('/run', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({code: document.getElementById('code').value})
        });
        const d = await r.json();
        document.getElementById('out').textContent = d.output || d.error;
      }
      </script>
    </body>
    </html>'''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))   
