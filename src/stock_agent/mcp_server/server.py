import logging
import sys

from mcp.server.fastmcp import FastMCP

from .. import tools

# Over stdio, stdout belongs to the protocol. Log to stderr only, and never print().
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format="%(levelname)s %(name)s: %(message)s")

mcp = FastMCP("stock-agent")
mcp.tool()(tools.get_prices)
mcp.tool()(tools.get_indicators)
mcp.tool()(tools.get_news)


def main():
    mcp.run()  # stdio transport by default


if __name__ == "__main__":
    main()