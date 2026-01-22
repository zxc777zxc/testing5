import os
import sys
import webbrowser
import subprocess


def main():
    os.makedirs("reports", exist_ok=True)
    report_path = os.path.abspath(os.path.join("reports", "report.html"))

    cmd = [
        sys.executable, "-m", "pytest",
        "-v",
        "--log-cli-level=INFO",
        "--show-capture=all",
        "--html=reports/report.html",
        "--self-contained-html",
    ]

    exit_code = subprocess.call(cmd)

    webbrowser.open(f"file:///{report_path}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
