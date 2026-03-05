%% ============================================================
%% Brainfuck runtime for SWI-Prolog
%% Tape: compound term t/30000 with nb_setarg for O(1) R/W
%% ============================================================

%% ---- 初期化 ----
init_tape :-
    functor(Tape, t, 30000),   % t(_, _, ..., _)  引数30000個
    nb_setval(bf_tape, Tape),
    nb_setval(bf_ptr,  1).

%% ---- セル読み書き（O(1)）----
get_cell(V) :-
    nb_getval(bf_ptr,  P),
    nb_getval(bf_tape, Tape),
    arg(P, Tape, V0),
    ( integer(V0) -> V = V0 ; V = 0 ).   % 未初期化セルは0扱い

set_cell(V) :-
    nb_getval(bf_ptr,  P),
    nb_getval(bf_tape, Tape),
    nb_setarg(P, Tape, V).               % インプレース破壊的書き込み

%% ---- ポインタ操作 ----
inc_ptr :- nb_getval(bf_ptr, P), P1 is P + 1, nb_setval(bf_ptr, P1).
dec_ptr :- nb_getval(bf_ptr, P), P1 is P - 1, nb_setval(bf_ptr, P1).

%% ---- セル演算 ----
inc_cell :- get_cell(V), V1 is (V + 1) mod 256, set_cell(V1).
dec_cell :- get_cell(V), V1 is (V - 1 + 256) mod 256, set_cell(V1).

%% ---- 入出力 ----
out_cell :-
    get_cell(V),
    char_code(C, V),
    put_char(C).

in_cell :-
    get_char(C),
    ( C = end_of_file -> Code = 0 ; char_code(C, Code) ),
    set_cell(Code).

%% ---- ループ条件ヘルパー ----
bf_cell_nonzero :- get_cell(V), V =\= 0.

%% ---- エントリポイント ----
:- initialization(main).
main :-
    init_tape,
