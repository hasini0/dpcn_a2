"""One command for everything:  python run_all.py your@email.com"""
import subprocess, sys
for step in (["collect.py", *sys.argv[1:3]], ["fetch_faculty.py"], ["build.py"], ["dashboard.py"], ["report.py"]):
    print("\n=== ", " ".join(step)); subprocess.run([sys.executable, *step], check=True)
print("\nDone. Submit files from the out/ folder.")
