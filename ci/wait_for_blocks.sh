#!/bin/bash
block_n=$(../src/defi-cli getblockchaininfo | jq '.blocks' )
while (($block_n < 10)) 
do
    echo $(../../src/defi-cli getblockchaininfo | jq '.')
done