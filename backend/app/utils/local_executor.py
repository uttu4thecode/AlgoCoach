import subprocess
import tempfile
import os
import time

LANGUAGE_EXTENSIONS = {
    "python": ".py",
    "javascript": ".js",
    "cpp": ".cpp",
    "c": ".c",
}

LANGUAGE_RUN_COMMANDS = {
    "python": ["python"],
    "javascript": ["node"],
    "cpp": ["./a.out"],
    "c": ["./a.out"],
}

async def run_code(source_code: str, language: str, stdin: str = "") -> dict:
    lang_lower = language.lower()
    
    if lang_lower not in LANGUAGE_EXTENSIONS:
        return {
            "error": f"Language '{language}' not supported",
            "status": "Error",
            "stdout": "",
            "stderr": f"Unsupported language: {language}",
            "compile_output": "",
            "time": None,
            "memory": None,
        }

    try:
        ext = LANGUAGE_EXTENSIONS[lang_lower]
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=ext,
            delete=False,
            dir=os.getcwd()
        ) as f:
            f.write(source_code)
            temp_file = f.name

        try:
            if lang_lower == "cpp":
                compile_result = subprocess.run(
                    ["g++", temp_file, "-o", "a.out"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if compile_result.returncode != 0:
                    return {
                        "status": "Compilation Error",
                        "stdout": "",
                        "stderr": compile_result.stderr,
                        "compile_output": compile_result.stderr,
                        "time": None,
                        "memory": None,
                    }
            elif lang_lower == "c":
                compile_result = subprocess.run(
                    ["gcc", temp_file, "-o", "a.out"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if compile_result.returncode != 0:
                    return {
                        "status": "Compilation Error",
                        "stdout": "",
                        "stderr": compile_result.stderr,
                        "compile_output": compile_result.stderr,
                        "time": None,
                        "memory": None,
                    }

            cmd = LANGUAGE_RUN_COMMANDS[lang_lower].copy()
            if lang_lower in ["python", "javascript"]:
                cmd.append(temp_file)

            start_time = time.time()
            result = subprocess.run(
                cmd,
                input=stdin,
                capture_output=True,
                text=True,
                timeout=5
            )
            elapsed = time.time() - start_time

            return {
                "status": "Accepted" if result.returncode == 0 else "Runtime Error",
                "stdout": result.stdout.strip() if result.stdout else "",
                "stderr": result.stderr.strip() if result.stderr else "",
                "compile_output": "",
                "time": f"{elapsed:.2f}",
                "memory": None,
            }

        finally:
            try:
                os.remove(temp_file)
            except:
                pass
            try:
                if lang_lower in ["cpp", "c"]:
                    os.remove("a.out")
            except:
                pass

    except subprocess.TimeoutExpired:
        return {
            "status": "Time Limit Exceeded",
            "stdout": "",
            "stderr": "Execution timeout (5 seconds)",
            "compile_output": "",
            "time": None,
            "memory": None,
        }
    except Exception as e:
        return {
            "status": "Error",
            "stdout": "",
            "stderr": str(e),
            "compile_output": "",
            "time": None,
            "memory": None,
        }
