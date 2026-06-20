import Data.IORef
import Data.Array.IO
import Data.Char (chr, ord)
import System.IO

main :: IO ()
main = do {
    hSetBuffering stdout NoBuffering;
    tape <- newArray (0, 29999) 0 :: IO (IOUArray Int Int);
    ptr <- newIORef 0;
    let { adjust d = do { p <- readIORef ptr; v <- readArray tape p; writeArray tape p ((v + d) `mod` 256) };
          output    = do { p <- readIORef ptr; v <- readArray tape p; putChar (chr v) };
          input     = do { p <- readIORef ptr; e <- isEOF; c <- if e then return 0 else fmap ord getChar; writeArray tape p c };
          whileNonZero body = do { p <- readIORef ptr; v <- readArray tape p; if v /= 0 then do { body; whileNonZero body } else return () } };
          