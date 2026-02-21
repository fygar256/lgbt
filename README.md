# Literal General Brainfuck Transpiler 'lgbt.py'

This is the Literal General Brainfuck Transpiler lgbt.py, which converts Brainfuck to various languages.

If there is a misunderstanding, it is no good so I explain that I am normal in sexuality.

I think this can translate to almost any language that has a while.

You can add line breaks by adding \n after the command you want to map.
The converted source is output to standard output, so please redirect it with bfac.py file.bf>filename.ext.

Transpiling from a high-level language to a lower-level language is generally difficult, but transpiling from a lower-level language to a higher-level language is easy.

Indentation is also performed automatically, so conversion to Python is also possible. By default, bfac.py converts to pseudo-assembly code. Specify the language to convert to using the map file described later. A header and footer will be required to run in the target language. Headers, footers, and map files for C and Python are provided.

# Sample

## C

### Map file

map.c.json

### Header

header.c

### Tailor

tailor.c

### Execution

```
bfac.py map.c.json header.c mandelbrot.bf tailor.c>out.c # Convert to C
cc out.c # Compile
a.out # Execution
```

## Python

### Map file

map.py.json

### Header file

header.py

### Tailor file

nothing

### Execution

```
bfac.py map.py.json header.py hello.bf > hello.py
python hello.py
```

By applying this, I think it can be used in a wide range of languages.

Ook and other languages ​​are also supported.
