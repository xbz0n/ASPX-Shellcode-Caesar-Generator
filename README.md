# ASPX Shellcode Ceasar Encrypted Generator 

This Python script automates the process of generating and inserting a shellcode into a C# file (ASPX-Helper.cs), then compiling it into an executable (ASPX-Helper.exe), which is subsequently run to produce an encoded version of the shellcode. This encoded shellcode is then inserted into an ASP.NET web shell template (webshell_template.aspx). Finally, a Metasploit resource file is created for quickly setting up a multi/handler to receive the reverse HTTPS Meterpreter shell.

## Functionality

The script performs the following steps:

1. Accepts user-provided LHOST and LPORT values via command line arguments.
2. Generates shellcode using msfvenom with the provided LHOST and LPORT values.
3. Embeds the generated shellcode into a template ASPX webshell.
4. Compiles a helper C# program that aids in the utilization of the shellcode.
5. Modifies the helper program to include the shellcode.
6. Runs the modified helper program to generate encoded shellcode.
7. Embeds the encoded shellcode into a webshell template and saves it as `WebShellFinal.aspx`.
8. Generates a Metasploit resource file `met64.rc` for handling incoming connections using the generated shellcode.

## Requirements

This script relies on the following software:

- Python 3
- Metasploit Framework
- Mono (for executing .NET applications)
- mcs (Mono C# compiler)

## Usage

Run the script using Python, providing the LHOST and LPORT values as command line arguments:

```bash
python3 aspx_shellcode_generator.py --LHOST your_ip --LPORT your_port
```

Replace `your_ip` and `your_port` with your local IP and desired port number respectively.

After the script completes, the generated shellcode, modified helper program, encoded shellcode, final webshell, and Metasploit resource file will be located in the `output` directory.

## Warning

Please note that this tool is for educational purposes and authorized testing only. Always obtain proper permission before performing any kind of penetration testing.

## License

This project is licensed under the MIT License. 

## Author

xbz0n

## Acknowledgments

This script was inspired by various resources in the penetration testing community.

## Disclaimer

The use of this script for illegal purposes is strictly prohibited. The author is not responsible for any misuse or damage caused by this script.
