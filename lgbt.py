#!/usr/bin/env python3

"""
Brainfuck Transpiler
Converts Brainfuck code to any language.

Usage:
  lgbt.py <file.bf>
  lgbt.py <mapfile> <file.bf>
  lgbt.py <mapfile> <headerfile> <file.bf>
  lgbt.py <mapfile> <headerfile> <file.bf> <tailfile>

openlabel / closelabel in the map file are replaced with unique loop labels.
"""

import sys
import json
from abc import ABC, abstractmethod


# ---------------------------------------------------------------------------
# デフォルト命令マッピング
# ---------------------------------------------------------------------------

DEFAULT_INSTRUCTIONS: dict[str, str] = {
    '>': "inc p\n",
    '<': "dec p\n",
    '+': "inc *p\n",
    '-': "dec *p\n",
    '.': "output\n",
    ',': "input\n",
    '[': "while *p\n",
    ']': "wend\n",
}


# ---------------------------------------------------------------------------
# 命令マッピングのロード
# ---------------------------------------------------------------------------

class InstructionLoader:
    """外部JSONファイルまたはデフォルトから命令マッピングを読み込む"""

    REQUIRED_KEYS = set('><+-.,[]')

    @classmethod
    def load(cls, mapfile: str) -> dict[str, str]:
        if mapfile == '':
            return DEFAULT_INSTRUCTIONS
        return cls._load_from_file(mapfile)

    @classmethod
    def _load_from_file(cls, mapfile: str) -> dict[str, str]:
        try:
            with open(mapfile, 'r') as fp:
                mapping: dict[str, str] = json.load(fp)
        except FileNotFoundError:
            print(f"Error: Map file '{mapfile}' not found", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in map file: {e}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        missing = cls.REQUIRED_KEYS - set(mapping.keys())
        if missing:
            print(f"Warning: Missing keys in map file: {missing}", file=sys.stderr)

        # リスト値は改行で結合して文字列に変換
        # 文字列値は空文字列でない場合のみ末尾に\nを付加 [BUG2修正]
        for k, v in mapping.items():
            if isinstance(v, list):
                mapping[k] = '\n'.join(str(e) for e in v) + '\n'
            elif isinstance(v, str) and v != '' and not v.endswith('\n'):
                mapping[k] = v + '\n'

        return mapping


# ---------------------------------------------------------------------------
# ループラベルの生成ユーティリティ
# ---------------------------------------------------------------------------

class LoopLabelGenerator:
    """ネストされたループ用のユニークなラベルを生成・管理する"""

    def __init__(self) -> None:
        self._stack: list[int] = []
        self._last_direction: str = '['   # '[' or ']'

    def enter_loop(self) -> str:
        """'[' を処理してラベル文字列を返す"""
        if self._last_direction == ']':
            self._stack[-1] += 1
        else:
            self._stack.append(1)
        self._last_direction = '['
        return self._format(self._stack)

    def exit_loop(self) -> str:
        """']' を処理してラベル文字列を返す"""
        # [BUG1修正] ポップを先に行ってからラベルを取得する
        if self._last_direction == ']':
            self._stack.pop()
        label = self._format(self._stack)
        self._last_direction = ']'
        return label

    @staticmethod
    def _format(stack: list[int]) -> str:
        return (
            str(stack)
            .replace(', ', '_')
            .replace('[', '')
            .replace(']', '')
        )


# ---------------------------------------------------------------------------
# トランスパイラ基底クラス
# ---------------------------------------------------------------------------

class BrainfuckTranspiler(ABC):
    """Brainfuck トランスパイラの基底クラス"""

    def __init__(self, instructions: dict[str, str]) -> None:
        self.instructions = instructions

    def transpile(self, headerfile: str, filename: str, tailfile: str) -> None:
        """ヘッダ・本体・テールの順に出力する"""
        self._print_file_raw(headerfile)
        self._process_bf_file(filename)
        self._print_file_raw(tailfile)

    def _process_bf_file(self, filename: str) -> None:
        if filename == '':
            return
        try:
            with open(filename, 'r') as fp:
                for char in fp.read():
                    self._handle_char(char)
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    @abstractmethod
    def _handle_char(self, char: str) -> None:
        """1文字のBrainfuck命令を処理する"""

    @staticmethod
    def _print_file_raw(filename: str) -> None:
        if filename == '':
            return
        try:
            with open(filename, 'r') as fp:
                for ch in fp.read():
                    print(ch, end='')
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


# ---------------------------------------------------------------------------
# 統合トランスパイラ（インデント付き変換 + openlabel / closelabel 置換）
# ---------------------------------------------------------------------------

class Transpiler(BrainfuckTranspiler):
    """インデント管理と openlabel / closelabel 置換を同時に行うトランスパイラ"""

    INDENT_UNIT = "    "
    INDENT_CHARS = frozenset('[')
    DEDENT_CHARS = frozenset(']')

    def __init__(self, instructions: dict[str, str]) -> None:
        super().__init__(instructions)
        self._indent_level = 0
        self._at_line_start = True
        self._label_gen = LoopLabelGenerator()

    def _handle_char(self, char: str) -> None:
        if char not in self.instructions:
            return

        if char in self.DEDENT_CHARS:
            self._indent_level = max(0, self._indent_level - 1)

        text = self.instructions[char]

        if char == '[':
            label = self._label_gen.enter_loop()
            text = text.replace("openlabel", f"LB{label}").replace("closelabel", f"LE{label}")
        elif char == ']':
            label = self._label_gen.exit_loop()
            text = text.replace("openlabel", f"LB{label}").replace("closelabel", f"LE{label}")

        self._emit(text)

        if char in self.INDENT_CHARS:
            self._indent_level += 1

    def _emit(self, text: str) -> None:
        for ch in text:
            if self._at_line_start and ch not in ('\n', '\r'):
                print(self.INDENT_UNIT * self._indent_level, end='')
                self._at_line_start = False
            print(ch, end='')
            if ch == '\n':
                self._at_line_start = True


# ---------------------------------------------------------------------------
# コマンドライン引数のパース
# ---------------------------------------------------------------------------

class ArgumentParser:
    """コマンドライン引数を解析してトランスパイラを構築するクラス"""

    def parse(self, argv: list[str]) -> tuple[BrainfuckTranspiler, str, str, str]:
        """(transpiler, headerfile, filename, tailfile) を返す"""
        args = argv[1:]

        if len(args) not in (1, 2, 3, 4):
            self._print_usage(argv[0])
            sys.exit(1)

        mapfile, headerfile, filename, tailfile = self._split_args(args)
        instructions = InstructionLoader.load(mapfile)
        return Transpiler(instructions), headerfile, filename, tailfile

    @staticmethod
    def _split_args(args: list[str]) -> tuple[str, str, str, str]:
        l = len(args)
        if l == 1:
            return '', '', args[0], ''
        if l == 2:
            return args[0], '', args[1], ''
        if l == 3:
            return args[0], args[1], args[2], ''
        return args[0], args[1], args[2], args[3]

    @staticmethod
    def _print_usage(prog: str) -> None:
        print(f"Usage: {prog} <file.bf>", file=sys.stderr)
        print(f"or   : {prog} <mapfile> <file.bf>", file=sys.stderr)
        print(f"or   : {prog} <mapfile> <headerfile> <file.bf>", file=sys.stderr)
        print(f"or   : {prog} <mapfile> <headerfile> <file.bf> <tailfile>", file=sys.stderr)


# ---------------------------------------------------------------------------
# エントリポイント
# ---------------------------------------------------------------------------

def main() -> None:
    parser = ArgumentParser()
    transpiler, headerfile, filename, tailfile = parser.parse(sys.argv)
    transpiler.transpile(headerfile, filename, tailfile)


if __name__ == '__main__':
    main()
