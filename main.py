import sys
import base64
import zlib
import lzma
import gzip
import marshal
import dis
import types
import argparse
import textwrap
import re

try:
    import uncompyle6
    HAS_UNCOMPYLE6 = True
except ImportError:
    HAS_UNCOMPYLE6 = False


def load_obfuscated(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    patterns = [
        r'exec\s*\(\s*["\']([^"\']+)["\']',
        r'exec\s*\(\s*"""(.*?)"""',
        r"exec\s*\(\s*'''(.*?)'''",
    ]
    for pat in patterns:
        m = re.search(pat, content, re.DOTALL)
        if m:
            return m.group(1)
    return content.strip()


def deobfuscate_pipeline(obfuscated: str):
    steps = [
        ("Reverse",  lambda s: s[::-1]),
        ("Base64",   lambda s: base64.b64decode(s + "=" * (4 - len(s) % 4) if len(s) % 4 else s)),
        ("Zlib",     zlib.decompress),
        ("LZMA",     lzma.decompress),
        ("Gzip",     gzip.decompress),
        ("Marshal",  marshal.loads),
    ]

    data = obfuscated
    for i, (name, fn) in enumerate(steps, 1):
        print(f"  [{i}/{len(steps)}] {name}...")
        try:
            data = fn(data)
        except Exception as e:
            raise RuntimeError(f"Step {name} failed: {e}") from e

    if isinstance(data, (bytes, bytearray)):
        return data.decode("utf-8", errors="replace"), "source"
    elif isinstance(data, str):
        return data, "source"
    else:
        return data, "code"


def handle_code_object(code_obj, output_path):
    out = open(output_path, "w", encoding="utf-8") if output_path else sys.stdout
    if HAS_UNCOMPYLE6:
        try:
            import io
            buf = io.StringIO()
            uncompyle6.code_deparse(code_obj, out=buf)
            print(buf.getvalue(), file=out)
            if output_path:
                out.close()
            return
        except Exception as e:
            print(f"  uncompyle6 could not decompile: {e}")
    print("\n[Byte-code — install uncompyle6 for source code]\n")
    dis.dis(code_obj)
    if output_path:
        out.close()


def main():
    parser = argparse.ArgumentParser(
        description="🔓 Python Deobfuscator (reverse→base64→zlib→lzma→gzip→marshal)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Примеры:
              python deobfuscator.py file.py
              python deobfuscator.py file.py -o result.py
              python deobfuscator.py --raw "ABCD..."
        """),
    )
    parser.add_argument("file", nargs="?", help="Obfuscated .py file")
    parser.add_argument("-o", "--output", help="Saved result in file")
    parser.add_argument("--raw", help="Pass string directly")
    parser.add_argument("--dis", action="store_true", help="Force show disassembler")
    args = parser.parse_args()

    if args.raw:
        obfuscated = args.raw
    elif args.file:
        obfuscated = load_obfuscated(args.file)
    else:
        parser.print_help()
        sys.exit(1)

    print(f"\n string length: {len(obfuscated)} symbols\n")

    try:
        result, kind = deobfuscate_pipeline(obfuscated)
    except RuntimeError as e:
        print(f"\n❌ {e}")
        print("Tip: Make sure the order of things matches the file..")
        sys.exit(1)

    print("\n Ready!\n" + "─" * 60)

    if kind == "source":
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result)
            print(f"Saved in: {args.output}")
        else:
            print(result)
    else:
        if args.dis:
            dis.dis(result)
        else:
            handle_code_object(result, args.output)
            if args.output:
                print(f"Saved in: {args.output}")


if __name__ == "__main__":
    main()
