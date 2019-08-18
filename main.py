from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers.lisp import SchemeLexer

from lispy import eof_object, eval, parse, to_string


def main(prompt="lispy> "):
    scheme_completer = WordCompleter(["begin", "call/cc"])
    session = PromptSession(
        lexer=PygmentsLexer(SchemeLexer), completer=scheme_completer
    )

    while True:
        try:
            text = session.prompt(prompt)
            x = parse(text)
            if x is eof_object:
                return
            val = eval(x)
            if val is not None:
                print(to_string(val))
        except KeyboardInterrupt:
            continue
        except EOFError:
            break
        except Exception as e:
            print(f"{type(e).__name__}: {e}")
    print("GoodBye!")


if __name__ == "__main__":
    main()
