import noderunner


def main():
    client = noderunner.Client()
    print("NodeRunner REPL")
    while True:
        inp = raw_input(">")
        if inp.strip() == "!quit":
            break
        ret = client.eval(inp)
        print(ret)

if __name__ == "__main__":
    main()
