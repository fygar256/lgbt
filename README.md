# Literal General Brainfuck Transpiler

This is 'lgbt.py', a Literal General Brainfuck Transpiler that converts Brainfuck to various languages.

I want to clarify that, just because the name is LGBT, there might be some misunderstanding, so I'm sexually normal. Alan Turing, who died young, was homosexual.

I believe it can convert to languages ​​that jump to any label (for example, assembly language) and almost any language with a while loop. It can also be applied to languages ​​that use line numbers to indicate jump destinations, like early BASIC.

The source code of the conversion result is output to standard output, so please use it by redirecting it as lgbt.py file.bf>filename.ext.

Generally, transpiling from a high-level language to a lower-level language is difficult, but transpiling from a lower-level language to a higher-level language is easy if you allow for some redundancy. Brainfuck is the lowest-level language, so it can be converted to almost any language. Furthermore, since it is Turing complete, it possesses computational versatility, and almost everything except special operations can be written in Brainfuck. Though it's not very practical.

It also automatically handles indentation, making conversion to Python possible. Even if a single Brainfuck instruction spans multiple lines in the target language, it can be written as a JSON list.

In the map file's target strings, `openlabel` and `closelabel` are replaced with the labels immediately before and after the corresponding `[',']` positions, respectively. `openline` and `closeline` are replaced with the line numbers of the corresponding `[',']` positions, respectively, with the line number at the `['` position and the line number after the `]` position.

If the `openline` token exists in the map file, line numbers are automatically added to the output.

By default, `lgbt.py` converts BF source code to pseudo-assembly code. Specify the language to convert to in the map file, which will be discussed later.

Headers and footers will likely be necessary for it to run in the target language system. It includes C, Python, Ruby, and bwbasic, as well as assembly files and headers, footers, and map files for x86_64 FreeBSD.

The number and interpretation of command-line arguments are as follows:

```
Number of arguments Interpretation
1 <file.bf>
2 <mapfile> <file.bf>
3 <mapfile> <headerfile> <file.bf>
4 <mapfile> <headerfile> <file.bf> <tailfile>
```

# Sample

## C

Map file:map.c.json

Header:header.c

Tailor:tailor.c

### Execution

```
lgbt.py map.c.json header.c mandelbrot.bf tailor.c>out.c # Convert to C
cc out.c # Compile
a.out # Execution
```

## Python

Map file:map.py.json

Header file:header.py

Tailor file:nothing

### Execution

```
lgbt.py map.py.json header.py hello.bf > hello.py
python hello.py
```

## Ruby

Map file:map.rb.json

Header file:header.rb

Tailor file:nothing

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

# Prolog
header:header.pl

tailor:tailor.pl

map:map.pl.json

### execution
```
lgbt.py map.pl.json header.pl hello.pl tailor.pl >hello.pl
swipl hello.pl
```

installation of swi-prolog required.

# Assembly example x86_64

```
lgbt.py map.amd64.json header.s hello.bf tailor.s > hello.s # Transform
as hello.s -o hello.o # Assemble
ld hello.o -o hello # Link
./hello # Execute
```

# Assembly of aarch64 (Fugaku super computer)

```
lgbt.py map.aarch64.json header.aarch64.s mandelbrot.bf tailor.aarch64.s > mandelbrot.aarch64.s
llvm-mc -triple=aarch64-unknown-freebsd -filetype=obj mandelbrot.aarch64.s -o mandelbrot.aarch64.o
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
lgbt.py map.bwbasic.json header.bwbasic hello.bf tailor.bwbasic>hello.bwbasic
bwbasic hello.bwbasic
Hello world!
```

Also, it seems that bwbasic can have issues like this. (Gemini)

3. [Important] Bugs specific to bwbasic (empty PRINT and consecutive execution)
A bug has been reported in bwbasic (especially older versions and certain builds) where, if certain processing is performed immediately after a PRINT statement, or if PRINT is repeated rapidly within a loop, extra line breaks (empty lines) are inserted due to a problem with the internal buffer processing.

By applying this, I think it can be used in a wide range of languages.

Ook and other languages ​​are also supported.

