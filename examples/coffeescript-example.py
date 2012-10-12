"""Example showing how to use coffeescript with noderunner
"""
from noderunner import Client

code = """test_fn = -> console.log('foo')"""


def main():
    cli = Client()

    ctx = cli.context("example", [("cs", "coffee-script")])

    res = ctx.call("cs", "compile", (code,))

    print(res)


if __name__ == "__main__":
    main()
