program brainfuck_output;

uses
  SysUtils;

var
  tape: array[0..29999] of Byte;
  ptr: Integer;
  inch: Char;

begin
  ptr := 0;
  FillChar(tape, SizeOf(tape), 0);
