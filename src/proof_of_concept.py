import asyncio
from argparse import ArgumentParser

def get_args():
    parser = ArgumentParser()

    return parser.parse_args()

async def main(args):
    pass

if __name__ == "__main__":
    args = get_args()
    asyncio.run(main(args))