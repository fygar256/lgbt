# Literal General Brainfuck Transpiler

This is the Literal General Brainfuck Transpiler 'lgbt.py', which translates Brainfuck into various languages.

Just to avoid any misunderstandings about my name being LGBT, I'll state that I'm sexually normal.

I believe it can translate any assembly language and almost any language that uses a while statement. While it doesn't work with languages ​​like BASIC, which use line numbers to indicate jump destinations, it can still translate if the statement uses a while statement.

Line breaks can be added by adding a \n after the target command.

The resulting source code is output to standard output; redirect it as lgbt.py file.bf>filename.ext.

While transpiling from a high-level language to a lower-level language is generally difficult, transpiling from a lower-level language to a higher-level language is easy.

When applied to general-purpose languages, indentation is automatically performed, so conversion to Python is also possible. Even if a single Brainfuck command spans multiple lines in the target language, you can write it with indentation by separating them with \n.

When using assembly language, ']', '[' specified in the conversion destination string in the map file will be replaced with the corresponding ']', '[' label.

By default, lgbt.py converts to pseudo-assembly code. The language to convert to can be specified in the map file described later.

Headers and footers will be required to run in the target language. Headers, footers, and map files for C, Python, Ruby, assembly, and x86_64 FreeBSD are provided.

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
lgbt.py map.c.json header.c mandelbrot.bf tailor.c>out.c # Convert to C
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
lgbt.py map.py.json header.py hello.bf > hello.py
python hello.py
```

## Ruby

### Map file

map.rb.json

### Header file

header.rb

### Tailor file

nothing

### Execution

```
lgbt.py map.rb.json header.rb hello.bf > hello.rb
ruby hello.rb
```

# Assembly example x86_64

Execution example

```
lgbt.py --asm map.amd64.json header.s hello.bf tailor.s > hello.s # Transform
as hello.s -o hello.o # Assemble
ld hello.o -o hello # Link
./hello # Execute
```

By applying this, I think it can be used in a wide range of languages.

Ook and other languages ​​are also supported.
