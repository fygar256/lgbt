# Literal General Brainfuck Transpiler
This is the Literal General Brainfuck Transpiler 'lgbt.py' that translates Brainfuck into various languages.

To avoid any misunderstandings about my name being LGBT, I'd like to state that I am sexually normal. Alan Turing, who died young, was homosexual.

I believe it can be translated into any assembly language and almost any language that uses a while statement. While it may not be applicable to languages ​​like BASIC, which use line numbers to indicate jump destinations, it can still be translated if the statement uses a while statement.

A newline can be added by adding a \n after the target command.

The translated source is output to standard output; redirect it as lgbt.py file.bf>filename.ext.

Transpiling from a high-level language to a lower-level language is generally difficult, but transpiling from a lower-level language to a higher-level language is easy. Brainfuck is the lowest-level language, so it can be translated into a variety of languages. Furthermore, since it is Turing complete, it has computational versatility, and all but specialized operations can be written in Brainfuck. It's not very practical, though.

When applied to general-purpose languages, indentation is automatic, making it possible to convert to Python. Even if a single Brainfuck command spans multiple lines in the target language, it can be written with indentation by separating them with \n.

In assembly language, ']' and '[' specified in the destination string of the map file are replaced with the corresponding ']' and '[' labels. LGBT only replaces the last '[' or ']' in the destination string of the map file with the jump destination label, so it can also be used with assembly languages ​​that use '[]', such as ARM64.

When performing label replacement, openlabel and closelabel in the destination string of the map file are replaced with the labels immediately before and after the corresponding '[' and ']', respectively.

The label replacement mode --label is easier to understand than the assembly mode --asm.

By default, lgbt.py converts bf source to pseudo-assembly code. The language to convert to can be specified in the map file described later.

Headers and footers will be required to run in the target language. Headers, footers, and map files for C, Python, Ruby, assembly, and x86_64 FreeBSD are provided.

The number of command line arguments and their interpretation are as follows:

### For general-purpose languages
```
Number of arguments Interpretation
1 <file.bf>
2 <mapfile> <file.bf>
3 <mapfile> <headerfile> <file.bf>
4 <mapfile> <headerfile> <file.bf> <tailfile>
```
### For assembly language

```
Number  arguments Interpretation
1 --asm <file.bf>
2 --asm <mapfile> <file.bf>
3 --asm <mapfile> <headerfile> <file.bf>
4 --asm <mapfile> <headerfile> <file.bf> <tailfile>
```

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

# Lisp
header:header.lisp

tailor:tailor.lisp

map:map.lisp.json

### execution

```
lgbt.py map.lisp.json header.lisp hello.bf tailor.lisp > hello.lisp
sbcl --script hello.lisp
```

installation of sbcl required.

# Assembly example x86_64

Execution example (--asm)

```
lgbt.py --asm map.amd64.json header.s hello.bf tailor.s > hello.s # Transform
as hello.s -o hello.o # Assemble
ld hello.o -o hello # Link
./hello # Execute
```

Execution example (--label)

```
lgbt.py --label map.amd64_2.json header.s hello.bf tailor.s > hello.s # Transform
as hello.s -o hello.o # Assemble
ld hello.o -o hello # Link
./hello # Execute
```

By applying this, I think it can be used in a wide range of languages.

Ook and other languages ​​are also supported.
