#!/usr/bin/env python3
"""
Brainfuck Transpiler
Converts Brainfuck code to any language.

Usage:
  lgbt.py [-l<N>] <suffix> <file.bf>

<suffix> selects the target files:
  map.<suffix>.json   (required; error if missing)
  header.<suffix>     (optional; treated as empty if missing)
  tailor.<suffix>     (optional; treated as empty if missing)

-l<N> sets the line-number step for line-based languages
  (e.g. -l10 -> 10,20,30...  -l20 -> 10,30,50...).
  Line numbers always start at 10. Default step is 10.
  Has effect only when the map file uses openline / closeline.

openlabel / closelabel in the map file are replaced with unique loop labels.
openline / closeline are replaced with line numbers for line-based languages.
"""
import sys
import os
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
        self._last_direction: str = '['

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

    def _print_file_raw(self, filename: str) -> None:
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
# 統合トランスパイラ（バッファリング付き）
# ---------------------------------------------------------------------------
class Transpiler(BrainfuckTranspiler):
    """インデント管理、openlabel/closelabel置換に加え、行番号処理を行うトランスパイラ"""
    INDENT_UNIT = "    "
    INDENT_CHARS = frozenset('[')
    DEDENT_CHARS = frozenset(']')

    def __init__(self, instructions: dict[str, str], line_step: int = 10) -> None:
        super().__init__(instructions)
        self._indent_level = 0
        self._at_line_start = True
        self._label_gen = LoopLabelGenerator()

        # 行番号の刻み幅（-l<N> で指定。既定は 10）
        self._line_step = line_step
        # 出力バッファ
        self._lines: list[str] = []
        self._current_line: list[str] = []
        
        # マップファイル内に行番号モード用のトークンが含まれているか判定
        self._use_line_numbers = any("openline" in v or "closeline" in v for v in instructions.values())
        
        # 各ループの開始行・終了行のインデックスを保持
        self._open_line_indices: dict[str, int] = {}
        self._close_line_indices: dict[str, int] = {}

    def _emit_char(self, ch: str) -> None:
        if ch == '\n':
            self._lines.append("".join(self._current_line))
            self._current_line = []
        else:
            self._current_line.append(ch)

    def _emit(self, text: str) -> None:
        for ch in text:
            if self._at_line_start and ch not in ('\n', '\r'):
                indent = self.INDENT_UNIT * self._indent_level
                for ic in indent:
                    self._emit_char(ic)
                self._at_line_start = False
            self._emit_char(ch)
            if ch == '\n':
                self._at_line_start = True

    def _handle_char(self, char: str) -> None:
        if char not in self.instructions:
            return

        if char in self.DEDENT_CHARS:
            self._indent_level = max(0, self._indent_level - 1)

        text = self.instructions[char]

        if char == '[':
            label = self._label_gen.enter_loop()
            
            text = text.replace("openlabel", f"LB{label}").replace("closelabel", f"LE{label}")
            text = text.replace("openline", f"__OL_{label}__").replace("closeline", f"__CL_{label}__")
            
            # Emit the '[' instruction first
            self._emit(text)
            # Record the CURRENT line index as openline (the line with the if/goto for '[')
            self._open_line_indices[label] = len(self._lines) - 1 if self._lines else 0
            
        elif char == ']':
            label = self._label_gen.exit_loop()
            
            text = text.replace("openlabel", f"LB{label}").replace("closelabel", f"LE{label}")
            text = text.replace("openline", f"__OL_{label}__").replace("closeline", f"__CL_{label}__")

            # Emit the ']' instruction
            self._emit(text)
            # For closeline: point to the line *after* this ']' instruction
            # This is crucial for empty loops `[]`
            self._close_line_indices[label] = len(self._lines)
            
        else:
            # For other commands, just emit
            self._emit(text)

        if char in self.INDENT_CHARS:
            self._indent_level += 1

    def _print_file_raw(self, filename: str) -> None:
        """ヘッダ・フッタに行番号を付加するためバッファへ出力するようオーバーライド"""
        if filename == '':
            return
        try:
            with open(filename, 'r') as fp:
                for ch in fp.read():
                    self._emit_char(ch)
                    if ch == '\n':
                        self._at_line_start = True
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    def transpile(self, headerfile: str, filename: str, tailfile: str) -> None:
        """ヘッダ・本体・テールの順にバッファリングし、最後に行番号を解決してフラッシュする"""
        self._print_file_raw(headerfile)
        # Ensure header's last line is completed if it didn't end with newline
        if self._current_line:
            self._lines.append("".join(self._current_line))
            self._current_line = []
            self._at_line_start = True
        self._process_bf_file(filename)
        self._print_file_raw(tailfile)
        self._flush()

    def _flush(self) -> None:
        """バッファされた行に対して行番号の付与とラベル解決を行って標準出力へ出す"""
        if self._current_line:
            self._lines.append("".join(self._current_line))
            self._current_line = []

        if self._use_line_numbers:
            # 10から始まり、-l<N>で指定した刻み幅で行番号を生成
            line_numbers = {i: 10 + i * self._line_step for i in range(len(self._lines) + 1)}

            for i, line in enumerate(self._lines):
                # プレースホルダが存在する場合のみ置換を試行
                if "__OL_" in line or "__CL_" in line:
                    for label, idx in self._open_line_indices.items():
                        target = f"__OL_{label}__"
                        if target in line:
                            line = line.replace(target, str(line_numbers[idx]))
                            
                    for label, idx in self._close_line_indices.items():
                        target = f"__CL_{label}__"
                        if target in line:
                            line = line.replace(target, str(line_numbers[idx]))

                print(f"{line_numbers[i]} {line}")
        else:
            # openline の指定がなければ元の挙動通り出力
            for line in self._lines:
                print(line)

# ---------------------------------------------------------------------------
# コマンドライン引数のパース
# ---------------------------------------------------------------------------
class ArgumentParser:
    """コマンドライン引数を解析してトランスパイラを構築するクラス"""
    def parse(self, argv: list[str]) -> tuple[BrainfuckTranspiler, str, str, str]:
        args = argv[1:]

        # `-l<N>` （または `-l <N>`）で行番号の刻み幅を指定する。
        # 省略時の既定値は 10。
        line_step = 10
        positional: list[str] = []
        i = 0
        while i < len(args):
            a = args[i]
            if a == '-l':
                # 分離形: -l 20
                i += 1
                if i >= len(args):
                    print("Error: -l requires a number", file=sys.stderr)
                    sys.exit(1)
                num = args[i]
            elif a.startswith('-l'):
                # 連結形: -l20
                num = a[2:]
            else:
                positional.append(a)
                i += 1
                continue

            try:
                line_step = int(num)
            except ValueError:
                print(f"Error: invalid line step '{num}'", file=sys.stderr)
                sys.exit(1)
            if line_step <= 0:
                print(f"Error: line step must be positive: {line_step}", file=sys.stderr)
                sys.exit(1)
            i += 1

        # `lgbt.py [-l<N>] <suffix> <file.bf>` の2つの位置引数を受け付ける。
        # （`lgbt.py <file.bf>` のデフォルト形式は廃止）
        if len(positional) != 2:
            self._print_usage(argv[0])
            sys.exit(1)

        suffix, filename = positional
        mapfile = f"map.{suffix}.json"
        headerfile = f"header.{suffix}"
        tailfile = f"tailor.{suffix}"

        # map ファイルは必須。なければエラー終了。
        if not os.path.isfile(mapfile):
            print(f"Error: Map file '{mapfile}' not found", file=sys.stderr)
            sys.exit(1)

        # header / tailor は任意。なければ空（出力なし）として扱う。
        if not os.path.isfile(headerfile):
            headerfile = ''
        if not os.path.isfile(tailfile):
            tailfile = ''

        instructions = InstructionLoader.load(mapfile)

        return Transpiler(instructions, line_step), headerfile, filename, tailfile

    @staticmethod
    def _print_usage(prog: str) -> None:
        print(f"Usage: {prog} [-l<N>] <suffix> <file.bf>", file=sys.stderr)
        print(f"  example: {prog} py hello.bf", file=sys.stderr)
        print(f"  example: {prog} -l20 bas hello.bf", file=sys.stderr)
        print(f"  uses map.<suffix>.json (required), "
              f"header.<suffix> / tailor.<suffix> (optional)", file=sys.stderr)
        print(f"  -l<N>: line-number step (start 10, default 10); "
              f"line-based targets only", file=sys.stderr)

# ---------------------------------------------------------------------------
# エントリポイント
# ---------------------------------------------------------------------------
def main() -> None:
    parser = ArgumentParser()
    transpiler, headerfile, filename, tailfile = parser.parse(sys.argv)
    transpiler.transpile(headerfile, filename, tailfile)

if __name__ == '__main__':
    main()
