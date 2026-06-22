import java.io.IOException;

class Main {
    static byte[] tape = new byte[30000];
    static int p = 0;

    static int input() throws IOException {
        int c = System.in.read();
        return c < 0 ? 0 : c;   // EOF -> 0
    }

    public static void main(String[] args) throws IOException {
