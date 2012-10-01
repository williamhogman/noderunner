import noderunner


def main():
    client = noderunner.Client()
    ret = client.eval("10+10")
    print(ret)

if __name__ == "__main__":
    main()
