;; header.lisp -- main とテープ初期化を定義
(defun main ()
  (let ((tape (make-array 30000 :initial-element 0))
        (ptr 0))
    ;; ここから Brainfuck 変換コードが挿入されます

