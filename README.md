# marhsal-deobfuscator
# Python Deobfuscator

A simple script to unpack and deobfuscate Python files. It automatically extracts data from `exec()` blocks, strips security layers, and restores the source code.

## 🔥 How It Works
The script strips encoding and compression layers step by step:
`Reverse` ➔ `Base64` ➔ `Zlib` ➔ `LZMA` ➔ `Gzip` ➔ `Marshal`

## 📦 Installation
To restore full source code, install the decompiler:
```bash
pip install uncompyle6
```
*If this library is missing, the script will output Python bytecode using the `dis` module instead.*

## 💻 Usage

* **Print result to terminal:**
  ```bash
  python decompiler.py obfuscated.py
  ```

* **Save clean code to a file:**
  ```bash
  python decompiler.py obfuscated.py -o clean.py
  ```

## 🛠 Arguments
* `input` — Path to the protected file.
* `-o`, `--output` — Path to save the decoded file (optional).
