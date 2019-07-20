# -*- coding: utf-8 -*-
from __future__ import annotations
import math
import typing

Symbol = str
isa = isinstance


class Env(dict):
    def __init__(self, parms=(), args=(), outer=None) -> None:
        self.update(zip(parms, args))
        self.outer = outer

    def find(self, var: str) -> Env:
        return self if var in self else self.outer.find(var)


def add_globals(env: Env) -> Env:
    "環境にScheme標準の手続きをいくつか追加する"
    import operator as op

    env.update(vars(math))  # sin, sqrt, ...
    env.update(
        {
            "+": op.add,
            "-": op.sub,
            "*": op.mul,
            "/": op.truediv,
            "not": op.not_,
            ">": op.gt,
            "<": op.lt,
            ">=": op.ge,
            "<=": op.le,
            "=": op.eq,
            "equal?": op.eq,
            "eq?": op.is_,
            "length": len,
            "cons": lambda x, y: [x] + y,
            "car": lambda x: x[0],
            "cdr": lambda x: x[1:],
            "append": op.add,
            "list": lambda *x: list(x),
            "list?": lambda x: isa(x, list),
            "null?": lambda x: x == [],
            "symbol?": lambda x: isa(x, Symbol),
        }
    )
    return env


global_env: Env = add_globals(Env())


# eval
def eval(x, env: Env = global_env):
    "環境の中で式を評価する。"
    if isa(x, Symbol):  # 変数参照
        return env.find(x)[x]
    elif not isa(x, list):  # 定数リテラル
        return x
    elif x[0] == "quote":  # (quote exp)
        (_, exp) = x
        return exp
    elif x[0] == "if":  # (if test conseq alt)
        (_, test, conseq, alt) = x
        return eval((conseq if eval(test, env) else alt), env)
    elif x[0] == "set!":  # (set! var exp)
        (_, var, exp) = x
        env.find(var)[var] = eval(exp, env)
    elif x[0] == "define":  # (define var exp)
        (_, var, exp) = x
        env[var] = eval(exp, env)
    elif x[0] == "lambda":  # (lambda (var*) exp)
        (_, vars, exp) = x
        return lambda *args: eval(exp, Env(vars, args, env))
    elif x[0] == "begin":  # (begin exp*)
        for exp in x[1:]:
            val = eval(exp, env)
        return val
    else:  # (proc exp*)
        exps = [eval(exp, env) for exp in x]
        proc = exps.pop(0)
        return proc(*exps)


def read(s: str):
    "文字列からScheme式を読み込む。"
    return read_from(tokenize(s))


parse = read


def tokenize(s: str) -> typing.List[str]:
    "文字列をトークンのリストに変換する。"
    return s.replace("(", " ( ").replace(")", " ) ").split()


def read_from(tokens: typing.List[str]):
    "トークンの列から式を読み込む。"
    if len(tokens) == 0:
        raise SyntaxError("unexpected EOF while reading")
    token = tokens.pop(0)
    if "(" == token:
        L = []
        while tokens[0] != ")":
            L.append(read_from(tokens))
        tokens.pop(0)  # pop off ')'
        return L
    elif ")" == token:
        raise SyntaxError("unexpected )")
    else:
        return atom(token)


def atom(token: str) -> typing.Union[Symbol, float]:
    "数は数にし、それ以外のトークンはシンボルにする。"
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return Symbol(token)


def to_string(exp):
    "PythonオブジェクトをLispの読める文字列に戻す。"
    return "(" + " ".join(map(to_string, exp)) + ")" if isa(exp, list) else str(exp)


def repl(prompt: str = "lis.py> ") -> None:
    "read-eval-print-loopのプロンプト"
    while True:
        val = eval(parse(input(prompt)))
        if val is not None:
            print(to_string(val))


if __name__ == "__main__":
    repl()
