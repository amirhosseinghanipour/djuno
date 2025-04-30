import subprocess
import os


def process_styles(styles: str) -> str:
    with open('temp.css', 'w') as f:
        f.write(styles)
    subprocess.run(['npx', 'postcss', 'temp.css', '-o', 'temp.out.css'])
    with open('temp.out.css', 'r') as f:
        processed = f.read()
    os.remove('temp.css')
    os.remove('temp.out.css')
    return processed
