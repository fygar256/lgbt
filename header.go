package main

import (
	"bufio"
	"io"
	"os"
)

var tape [30000]byte
var p int
var reader = bufio.NewReader(os.Stdin)

func input() byte {
	b, err := reader.ReadByte()
	if err == io.EOF {
		return 0 // EOF -> 0
	}
	if err != nil {
		panic(err)
	}
	return b
}

func main() {
