# Sample

## C

The default target language is C, so no map file is required.

Header

header.c
```
#include <stdio.h>
void main() {
char array[30000]={0};
char *ptr=array;
```

Tailor

tailor.c

```
}
```

## Execution

```
bfac.py header.c mandelbrot.bf tailor.c>out.c # Convert to C
cc out.c # Compile
a.out # Execute
```

## Python

Header File

header.py

```
import sys
ptr=0
tape=[0]*30000
```

Map File

map.py.json
```
{
">": "ptr += 1\n",
"<": "ptr -= 1\n",
"+": "tape[ptr] = (tape[ptr] + 1) & 0xFF\n",
"-": "tape[ptr] = (tape[ptr] - 1) & 0xFF\n",
".": "sys.stdout.write(chr(tape[ptr]))\n",
",": "tape[ptr] = ord(sys.stdin.read(1))\n",
"[": "while tape[ptr]:\n",
"]": ""
}
```

Execution

```
bfac.py -m map.py.json header.py hello.bf > hello.py
python hello.py
```
This should support a wide range of languages.

It also works with Ook.
