import noderunner as nr


def main():
    bn = nr.BlockingNode()
    line = str()
    print("NodeRunner REPL")
    while True:
        line = raw_input(">")
        if line == ":quit":
            break
        res,error = bn.eval(line)
        if res:
            print(res)
        elif error:
            print(error)

if __name__ == "__main__":
    main()
