"""Example showing how to use coffeescript with noderunner
"""
from noderunner import Client

code = """test_fn = -> console.log('foo')"""


def main():
    cli = Client()

    ctx = cli.context("example", [("cs", "coffee-script")])

    ctx.set("code", code)

    res = ctx.eval("cs.compile(code)")

    print(res)


if __name__ == "__main__":
    main()
