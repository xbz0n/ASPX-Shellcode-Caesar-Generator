using System;
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
            // Insert your shellcode here as a byte array
            // The shellcode should be inserted in the form of a byte array buf[]
            // For example: byte[] buf = new byte[] {0xfc, 0x48, 0x83, ... };
            !!!SHELLCODE!!!

            // Declare a new byte array of the same length as the shellcode
            byte[] encoded = new byte[buf.Length];

            // Encode each byte of the shellcode by adding 5 to it modulo 256 (Caesar Cipher with a shift of 5)
            for (int i = 0; i < buf.Length; i++)
            {
                encoded[i] = (byte)(((uint)buf[i] + 5) & 0xFF);
            }

            // Initialize a StringBuilder to build a string of the encoded shellcode bytes in hexadecimal format
            StringBuilder hex = new StringBuilder(encoded.Length * 2);
            foreach (byte b in encoded)
            {
                // Append each byte as a hexadecimal string
                hex.AppendFormat("0x{0:x2},", b);
            }

            // Write the encoded shellcode string to a file named "encoded_shellcode.txt"
            File.WriteAllText("encoded_shellcode.txt", hex.ToString());

            // Read the content of the "encoded_shellcode.txt" file
            string fileContent = File.ReadAllText("encoded_shellcode.txt");

            // Print the content of the "encoded_shellcode.txt" file to the console
            Console.WriteLine("The payload is: " + fileContent);
        }
    }
}
