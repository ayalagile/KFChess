"""
Entry point - קורא את stdin ומריץ את ה-script.
"""

from text_test.script_runner import run_script

def main():
    lines = []
    while True:
        try:
            lines.append(input().strip())
        except EOFError:
            break
    run_script(lines)

if __name__ == "__main__":
    main()