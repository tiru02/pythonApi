from flask import Flask, request, jsonify
import subprocess
import tempfile
import uuid
import os
import sys

app = Flask(__name__)

PYTHON_BIN = sys.executable  # uses Vercel's Python


@app.route("/run/python", methods=["POST"])
def run_python():
    data = request.get_json()
    code = data.get("code")

    if not code:
        return jsonify({"error": "No code provided"}), 400

    run_id = str(uuid.uuid4())

    with tempfile.TemporaryDirectory() as tmp:
        code_path = os.path.join(tmp, "main.py")

        with open(code_path, "w") as f:
            f.write(code)

        try:
            result = subprocess.run(
                [PYTHON_BIN, code_path],
                capture_output=True,
                text=True,
                timeout=3,
                env={},
            )

            return jsonify({
                "status": "SUCCESS" if result.returncode == 0 else "RUNTIME_ERROR",
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode
            })

        except subprocess.TimeoutExpired:
            return jsonify({
                "status": "TIME_LIMIT_EXCEEDED",
                "stdout": "",
                "stderr": "Execution timed out",
                "exit_code": 124
            })


# if __name__ == "__main__":
#     app.run()
