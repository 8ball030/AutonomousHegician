#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Tom Rae
Authorised use only
"""
import json

import requests


class DexWrapper:
    BASE_URL = "https://api.1inch.exchange/v1.1/"
    ALLOWED_DEXS = ["uniswap"]

    def get_ticker(self, base, counter):
        amt = 10000_000_000_000_000_000_000
        path = f"quote?fromTokenSymbol={base}&toTokenSymbol={counter}&amount={amt}"
        res = json.loads(requests.get(self.BASE_URL + path).content)
        buy_amount = float(int(res["fromTokenAmount"])) / (
            10 ** res["fromToken"]["decimals"]
        )
        to_amount = float(int(res["toTokenAmount"])) / (
            10 ** res["toToken"]["decimals"]
        )
        r1 = buy_amount / to_amount
        return r1


def main():
    """Run the main method."""
    dex = DexWrapper()
    dex.get_ticker("DAI", "ETH")
    pass


if __name__ == "__main__":
    main()
