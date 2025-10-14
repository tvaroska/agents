import subprocess
import tempfile
import os

MESSAGE = "Create simple python script - Hello world in test.py. Add inline script metadata and use all best practices, this script is to learn python. Test script for syntax correctnes"

# Create a temporary directory
temp_dir = tempfile.mkdtemp()
result_file = os.path.join(temp_dir, 'result.txt')

# Run gemini command and capture output
result = subprocess.run(['gemini', f'-p "{MESSAGE}"', '-y'], stdout=subprocess.PIPE)

# Save output to result.txt
with open(result_file, 'wb') as f:
    f.write(result.stdout)

print(f"Output saved to: {result_file}")
print(f"Temporary directory: {temp_dir}")
