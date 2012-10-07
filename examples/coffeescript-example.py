"""Example showing how to use coffeescript with noderunner
"""

import json

from noderunner import Client

code = """

test_fn = -> console.log('foo')

"""


def main():
    cli = Client()

    ctx = cli.context("lol", [["cs", "coffee-script"]])
    ctx.eval("var code = "+json.dumps(code)+";")
    
    ret = ctx.eval("cs.compile(code)")
    print ret


if __name__ == "__main__":
    main()
