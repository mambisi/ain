#!/usr/bin/env python3
# Copyright (c) 2014-2019 The Bitcoin Core developers
# Copyright (c) DeFi Blockchain Developers
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.
"""Test pool's RPC.

- verify basic accounts operation
"""

from test_framework.test_framework import DefiTestFramework

from test_framework.authproxy import JSONRPCException
from test_framework.util import assert_equal, \
    connect_nodes_bi

import random

class PoolSwapTest (DefiTestFramework):
    def set_test_params(self):
        self.num_nodes = 3
        # node0: main
        # node1: secondary tester
        # node2: revert create (all)
        self.setup_clean_chain = True
        self.extra_args = [['-txnotokens=0'], ['-txnotokens=0'], ['-txnotokens=0']]

        # Set parameters for create tokens and pools
        self.count_pools = 1     # 10
        self.count_account = 10  # 1000
        self.commission = 0.001

        self.amount_token = 1000
        self.tokens = []

        self.accounts = []

    # TODO TODO TODO
    def get_id_token(self, symbol):
        list_tokens = self.nodes[0].listtokens()
        for idx, token in list_tokens.items():
            if (token["symbol"] == symbol):
                return str(idx)

    def generate_accounts(self):
        for i in range(self.count_account):
            self.accounts.append(self.nodes[0].getnewaddress("", "legacy"))

    def create_token(self, symbol, address):
        self.nodes[0].createtoken([], {
            "symbol": symbol,
            "name": "Token " + symbol,
            "isDAT": False,
            "collateralAddress": address
        })
        self.nodes[0].generate(1)
        self.tokens.append(symbol)

    def create_pool(self, tokenA, tokenB, owner):
        self.nodes[0].createpoolpair({
            "tokenA": tokenA,
            "tokenB": tokenB,
            "commission": self.commission,
            "status": True,
            "ownerFeeAddress": owner
        }, [])
        self.nodes[0].generate(1)

    def create_pools(self, owner):
        for i in range(self.count_pools):
            tokenA = "GOLD" + str(i)
            tokenB = "SILVER" + str(i)
            self.create_token(tokenA, owner)
            self.create_token(tokenB, owner)

            print("create")

            tokenA = tokenA + "#" + self.get_id_token(tokenA)
            tokenB = tokenB + "#" + self.get_id_token(tokenB)
            print(tokenA)
            self.create_pool(tokenA, tokenB, owner)

    def mint_tokens(self, owner):
        mint_amount = str(self.count_account * self.amount_token)

        for item in self.tokens:
            self.nodes[0].sendmany("", { owner : 0.02 })
            self.nodes[0].generate(1)
            self.nodes[0].minttokens([], mint_amount + "@" + self.get_id_token(item))
            self.nodes[0].generate(1)

        return mint_amount

    def send_tokens(self, owner):
        send_amount = str(self.amount_token)
        for token in self.tokens:

            start = 0
            step = 12

            while True:
                outputs = {}

                end = 0
                if start + step > self.count_account:
                    end = self.count_account
                else:
                    end = start + step
                for idx in range(start, end):
                    outputs[self.accounts[idx]] = send_amount + "@" + self.get_id_token(token)

                self.nodes[0].sendmany("", { owner : 0.02 })
                self.nodes[0].generate(1)

                self.nodes[0].accounttoaccount([], owner, outputs)
                self.nodes[0].generate(1)

                if start + step < self.count_account:
                    start += step
                    print("send " + str(start))
                else:
                    print("send " + str(end))
                    break

    def add_liquidity(self, account, amountA, amountB):
        self.nodes[0].sendmany("", { account : 0.02 })
        self.nodes[0].generate(1)

        self.nodes[0].addpoolliquidity({
            account: [amountA, amountB]
        }, account, [])
        self.nodes[0].generate(1)

    def add_pools_liquidity(self, owner):
        for item in range(self.count_pools):
            tokenA = "GOLD" + str(item)
            tokenB = "SILVER" + str(item)

            for account in self.accounts:
                amountA = str(random.randint(1, self.amount_token / 2)) + "@" + self.get_id_token(tokenA)
                amountB = str(random.randint(1, self.amount_token / 2)) + "@" + self.get_id_token(tokenB)
                self.add_liquidity(account, amountA, amountB)
                print("add liquidity " + amountA + " | " + amountB)

    def pollswap(self):
        for item in range(self.count_pools):
            tokenA = "GOLD" + str(item)
            tokenB = "SILVER" + str(item)

            for account in self.accounts:
                self.nodes[0].sendmany("", { account : 0.02 })
                self.nodes[0].generate(1)

                self.nodes[0].poolswap({
                    "from": account,
                    "tokenFrom": self.get_id_token(tokenB),
                    "amountFrom": 10,
                    "to": account,
                    "tokenTo": str(self.get_id_token(tokenA)),
                }, [])
                self.nodes[0].generate(1)

    def run_test(self):
        assert_equal(len(self.nodes[0].listtokens()), 1) # only one token == DFI

        print("Generating initial chain...")

        self.nodes[0].generate(100)
        self.sync_all()

        # Stop node #2 for future revert
        self.stop_node(2)

        owner = self.nodes[0].getnewaddress("", "legacy")
        self.nodes[0].generate(1)

        # START
        #========================
        print("Generating accounts...")
        self.generate_accounts()
        assert_equal(len(self.accounts), self.count_account)
        print("Generate " + str(self.count_account) + " accounts")

        print("Generating pools...")
        self.create_pools(owner)
        assert_equal(len(self.nodes[0].listtokens({}, False)), self.count_pools * 3)
        assert_equal(len(self.nodes[0].listpoolpairs({}, False)), self.count_pools)
        print("Generate " + str(self.count_pools) + " pools and " + str(self.count_pools * 2) + " tokens")

        print("Minting tokens...")
        mint_amount = self.mint_tokens(owner)
        assert_equal(len(self.nodes[0].getaccount(owner, {}, True)), self.count_pools * 2)
        print("Minted " + mint_amount + " of every coin")

        print("Sending tokens...")
        self.send_tokens(owner)
        # TODO check
        print("Tokens sent out")

        print("Adding liquidity...")
        self.add_pools_liquidity(owner)
        # TODO check
        print("Liquidity added")

        print("Swapping tokens...")
        self.pollswap()
        # TODO check
        print("Tokens exchanged")

        # REVERTING:
        #========================
        print ("Reverting...")
        self.start_node(2)
        self.nodes[2].generate(20)

        connect_nodes_bi(self.nodes, 1, 2)
        self.sync_blocks()

        #assert_equal(self.nodes[0].getaccount(accountGold, {}, True)[idGold], initialGold)
        #assert_equal(self.nodes[0].getaccount(accountSilver, {}, True)[idSilver], initialSilver)

        assert_equal(len(self.nodes[0].getrawmempool()), 0) # 4 txs


if __name__ == '__main__':
    PoolSwapTest ().main ()
