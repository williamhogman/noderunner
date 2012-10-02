import noderunner


def main():
    client = noderunner.Client()
    ctx = client.context("repl")
    print("NodeRunner REPL")
    while True:
        inp = raw_input(">")
        if inp.strip() == "!quit":
            break
        ret = ctx.eval(inp)
        print(ret)


if __name__ == "__main__":
    main()
