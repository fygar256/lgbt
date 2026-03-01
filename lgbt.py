#!/usr/bin/env python3

"""
Brainfuck Transpiler
Converts Brainfuck code to any language.

Usage (generic mode):
  lgbt.py <file.bf>
  lgbt.py <mapfile> <file.bf>
  lgbt.py <mapfile> <headerfile> <file.bf>
  lgbt.py <mapfile> <headerfile> <file.bf> <tailfile>

Usage (assembly mode):
  lgbt.py --asm <file.bf>
  lgbt.py --asm <mapfile> <file.bf>
  lgbt.py --asm <mapfile> <headerfile> <file.bf>
  lgbt.py --asm <mapfile> <headerfile> <file.bf> <tailfile>

Usage (label mode):
  lgbt.py --label <file.bf>
  lgbt.py --label <mapfile> <file.bf>
  lgbt.py --label <mapfile> <headerfile> <file.bf>
  lgbt.py --label <mapfile> <headerfile> <file.bf> <tailfile>

In assembly mode, the map values for '[' and ']' may contain ']' and '['
as placeholders respectively; these are replaced with generated loop labels.
"""

import sys
import json

# デフォルトの命令マッピング（汎用モード）
DEFAULT_INSTRUCTIONS = {
    '>': "inc p\n",
    '<': "dec p\n",
    '+': "inc *p\n",
    '-': "dec *p\n",
    '.': "output\n",
    ',': "input\n",
    '[': "while *p\n",
    ']': "wend\n"
}

instructions = {}

state = {'lf': '[', 'loopstack': []}

def load_instructions(mapfile):
    """外部JSONファイルから命令マッピングを読み込む"""
    if mapfile == '':
        return DEFAULT_INSTRUCTIONS
    try:
        with open(mapfile, 'r') as fp:
            mapping = json.load(fp)
        required_keys = set('><+-.,[]')
        missing = required_keys - set(mapping.keys())
        if missing:
            print(f"Warning: Missing keys in map file: {missing}", file=sys.stderr)
        return mapping
    except FileNotFoundError:
        print(f"Error: Map file '{mapfile}' not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in map file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def print_file_raw(fp):
    for ch in fp.read():
        print(ch, end='')

def operationla(filenameh,filename,filenamet,bf_char):
    if filenameh != '':
        try:
            with open(filenameh, 'r') as fp:
                print_file_raw(fp)
        except FileNotFoundError:
            print(f"Error: File '{filenameh}' not found", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    if filename != '':
        try:
            with open(filename, 'r') as fp:
                for char in fp.read():
                    bf_char(char)
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    if filenamet != '':
        try:
            with open(filenamet, 'r') as fp:
                print_file_raw(fp)
        except FileNotFoundError:
            print(f"Error: File '{filenamet}' not found", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

def _lsout(loopstack):
    """ループスタックをラベル名用の文字列に変換する"""
    return str(loopstack).replace(', ', '_').replace('[', '').replace(']', '')

def print_bf_char_asm(char):
    global state
    if char not in instructions:
        return

    text = instructions[char]

    if char == '[':
        ls = state['loopstack']
        if state['lf'] == ']':
                ls[-1] += 1
        else:
            ls.append(1)
        state['lf'] = '['
        label = _lsout(ls)
        print(f"LB{label}:")
        s=f"LE{label}"
        new_text = s.join(text.rsplit("]", 1))
        print(new_text)

    elif char == ']':
        ls = state['loopstack']
        if state['lf'] == ']':
            ls.pop()
        state['lf'] = ']'
        label = _lsout(ls)
        s=f"LB{label}"
        new_text = s.join(text.rsplit("[", 1))
        print(new_text)
        print(f"LE{label}:")

    else:
        print(text, end='')

def print_bf_char_label(char):
    global state
    if char not in instructions:
        return

    text = instructions[char]

    if char == '[':
        ls = state['loopstack']
        if state['lf'] == ']':
            ls[-1] += 1
        else:
            ls.append(1)
        state['lf'] = '['
        label = _lsout(ls)
        so=f"LB{label}"
        sc=f"LE{label}"
        text = text.replace("openlabel", so)
        new_text = text.replace("closelabel", sc)
        print(new_text)

    elif char == ']':
        ls = state['loopstack']
        if state['lf'] == ']':
            ls.pop()
        state['lf'] = ']'
        label = _lsout(ls)
        so=f"LB{label}"
        sc=f"LE{label}"
        text = text.replace("openlabel", so)
        new_text = text.replace("closelabel", sc)
        print(new_text)

    else:
        print(text, end='')

# ---------------------------------------------------------------------------
# 汎用モード（インデント付き変換）
# ---------------------------------------------------------------------------

def emit(text, indent_level, indent_unit, at_line_start):
    """テキストを出力する。改行のたびに次の行頭へインデントを挿入する。"""
    for ch in text:
        if at_line_start and ch not in ('\n', '\r'):
            print(indent_unit * indent_level, end='')
            at_line_start = False
        print(ch, end='')
        if ch == '\n':
            at_line_start = True
    return at_line_start

def convert_generic(filenameh, filename, filenamet):
    """汎用モード: インデントを管理しながら変換する"""
    indent_unit = "    "
    indent_chars = "["
    dedent_chars = "]"
    use_indent = bool(indent_unit)

    indent_level = 0
    at_line_start = True

    def print_bf_char_generic(char, indent_level, at_line_start):
        if char not in instructions:
            return indent_level, at_line_start

        if use_indent and char in dedent_chars:
            indent_level = max(0, indent_level - 1)

        text = instructions[char]
        if use_indent:
            at_line_start = emit(text, indent_level, indent_unit, at_line_start)
        else:
            print(text, end='')

        if use_indent and char in indent_chars:
            indent_level += 1

        return indent_level, at_line_start

    if filenameh != '':
        try:
            with open(filenameh, 'r') as fp:
                print_file_raw(fp)
        except FileNotFoundError:
            print(f"Error: File '{filenameh}' not found", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    if filename != '':
        try:
            with open(filename, 'r') as fp:
                for char in fp.read():
                    print_bf_char_generic(char,indent_level,at_line_start)
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    if filenamet != '':
        try:
            with open(filenamet, 'r') as fp:
                print_file_raw(fp)
        except FileNotFoundError:
            print(f"Error: File '{filenamet}' not found", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

# ---------------------------------------------------------------------------
# アセンブリモード（ループラベル生成）
# ---------------------------------------------------------------------------


def convert_asm(filenameh, filename, filenamet):
    """アセンブリモード: '[' / ']' にループラベルを生成して変換する"""

    # ループラベル管理

    operationla(filenameh,filename,filenamet,print_bf_char_asm)

# ---------------------------------------------------------------------------
# ラベルモード（ループラベル生成）
# ---------------------------------------------------------------------------


def convert_label(filenameh, filename, filenamet):
    """'[' / ']' の'label'を対応する大括弧のラベルに置換して変換する"""

    # ループラベル管理

    operationla(filenameh,filename,filenamet,print_bf_char_label)


# ---------------------------------------------------------------------------
# エントリポイント
# ---------------------------------------------------------------------------

def main():
    args = sys.argv[1:]

    # --asm or --label フラグの検出
    asm_mode = False
    label_mode = False
    if args and args[0] == '--asm':
        asm_mode = True
        args = args[1:]
    elif args and args[0] == '--label':
        label_mode = True
        args = args[1:]


    l = len(args)
    if l not in (1, 2, 3, 4):
        prog = sys.argv[0]
        print(f"Usage: {prog} [--asm|--label] <file.bf>", file=sys.stderr)
        print(f"or   : {prog} [--asm|--label] <mapfile> <file.bf>", file=sys.stderr)
        print(f"or   : {prog} [--asm|--label] <mapfile> <headerfile> <file.bf>", file=sys.stderr)
        print(f"or   : {prog} [--asm|--label] <mapfile> <headerfile> <file.bf> <tailfile>", file=sys.stderr)
        sys.exit(1)

    if l == 1:
        mapfile, filenameh, filename, filenamet = '', '', args[0], ''
    elif l == 2:
        mapfile, filenameh, filename, filenamet = args[0], '', args[1], ''
    elif l == 3:
        mapfile, filenameh, filename, filenamet = args[0], args[1], args[2], ''
    else:  # l == 4
        mapfile, filenameh, filename, filenamet = args[0], args[1], args[2], args[3]

    global instructions
    instructions = load_instructions(mapfile)

    if asm_mode:
        convert_asm(filenameh, filename, filenamet)
    elif label_mode:
        convert_label(filenameh, filename, filenamet)
    else:
        convert_generic(filenameh, filename, filenamet)


if __name__ == '__main__':
    main()
