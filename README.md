---
title: General-Purpose Brainfuck Transpiler 'lgbt.py'
tags: Brainf*ck Python C Terminal Transpiler
author: fygar256
slide: false
---

Literal General Brainfuck Transpiler

This is 'lgbt.py', a Literal General Brainfuck Transpiler that converts Brainfuck to various languages.

I want to clarify that, just because the name is LGBT, there might be some misunderstanding, so I'm normal in terms of sexuality. Alan Turing, who died young, was homosexual.

I believe it can convert to languages ​​that jump to any label (for example, assembly language) and almost any language with `while` loops. It can also be applied to languages ​​that use line numbers to indicate jump destinations, like early BASIC.

The source code of the conversion result is output to standard output, so please use redirection with `lgbt.py file.bf>filename.ext`.

Generally, transpiling from a high-level language to a lower-level language is difficult, but transpiling from a lower-level language to a higher-level language is easy if you can tolerate some redundancy. Brainfuck is the lowest-level language, so it can be translated into virtually any language. Furthermore, it is Turing complete, possessing computational versatility; almost everything except special operations can be written in Brainfuck. Though it's not very practical.

It also automatically handles indentation, making conversion to Python possible. Even if a single Brainfuck instruction spans multiple lines in the target language, it can be written as a JSON list.

For languages ​​that use labels, such as assembly, `openlabel` and `closelabel` in the map file's target string are replaced with the labels immediately before and after the corresponding '[',']' positions, respectively.

In languages ​​that use line numbers to indicate jump destinations, such as early BASIC, `openline` and `closeline` are replaced with the line numbers at the position of the corresponding `[` and `]`, respectively.

If the `openline` token exists in the map file, line numbers will be automatically added to the output.

To run lgbt.py, you need a mapfile, headerfile, and tailorfile for each language.

The naming convention for each file is as follows:

```
map.suffix.json # mapfile
header.suffix # headerfile
tailor.suffix # tailorfile
```

For sample and practical use, headers, footers, and map files for C, Python, Ruby, bwbasic, assembly, and x86_64 FreeBSD are included.

The command-line arguments and their interpretation are as follows:

```
lgbt.py <suffix> <file.bf>
```
# Sample

## C

Map file:map.c.json

Header:header.c

Tailor:tailor.c

### Execution

```
lgbt.py c mandelbrot.bf >out.c # Convert to C
cc out.c # Compile
a.out # Execution
```

## Python

Map file:map.py.json

Header file:header.py

Tailor file:nothing

### Execution

```
lgbt.py py hello.bf > hello.py
python hello.py
```

## Ruby

Map file:map.rb.json

Header file:header.rb

Tailor file:nothing

### Execution

```
lgbt.py rb hello.bf > hello.rb
ruby hello.rb
```

# Lisp
header:header.lisp

tailor:tailor.lisp

map:map.lisp.json

### execution

```
lgbt.py lisp hello.bf > hello.lisp
sbcl --script hello.lisp
```

installation of sbcl required.

# Prolog
header:header.pl

tailor:tailor.pl

map:map.pl.json

### execution
```
lgbt.py pl hello.bf >hello.pl
swipl hello.pl
```

installation of swi-prolog required.

## haskell

Map file:map.hs.json

Header:header.hs

Tailor:tailor.hs

### Execution

```
lgbt.py hs mandelbrot.bf >out.hs # Convert to Haskell
ghc out.hs -o out # Compile
out # Execution
```

# Assembly example x86_64

```
lgbt.py s hello.bf > hello.s # Transform
as hello.s -o hello.o # Assemble
ld hello.o -o hello # Link
./hello # Execute
```

# Assembly of aarch64 (Fugaku super computer)

```
lgbt.py aarch64 mandelbrot.bf > mandelbrot.aarch64
llvm-mc -triple=aarch64-unknown-freebsd -filetype=obj mandelbrot.aarch64 -o mandelbrot.aarch64.o
```


### Example of line number jump (bwbasic)

Map file

```json: map.bwbasic.json
{
">": "ptr=ptr+1",
"<": "ptr=ptr-1",
"+": "array(ptr)=(array(ptr)+1) mod 256",
"-": "array(ptr)=(array(ptr)-1) mod 256",
".": "print chr$(array(ptr));",
",": [ "do",
" a$=inkey$",
"loop while a$=\"\"",
"array(ptr)=asc(a$)" ],
"[": "if array(ptr)=0 then goto closeline",

"]": "goto openline"
}
```

Header file
```text:header.bwbasic
dim array(30000)
ptr=0
```

Tailor file
```text:tailor.bwbasic
end
```

Execution
```
lgbt.py bwbasic hello.bf >hello.bwbasic
bwbasic hello.bwbasic
Hello world!
```

Also, it seems that bwbasic can have issues like this. (Gemini)

3. [Important] Bugs specific to bwbasic (empty PRINT and consecutive execution)
A bug has been reported in bwbasic (especially older versions and certain builds) where, if certain processing is performed immediately after a PRINT statement, or if PRINT is repeated rapidly within a loop, extra line breaks (empty lines) are inserted due to a problem with the internal buffer processing.

By applying this, I think it can be used in a wide range of languages.

Ook and other languages ​​are also supported.

