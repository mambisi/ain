#!/bin/bash
block_n=$(./src/defi-cli getblockchaininfo | jq '.blocks' )
echo $block_n
echo $(./src/defi-cli getblockchaininfo | jq '.' )
while [ "$block_n" -lt 10 ] 
do
    echo $(./src/defi-cli getblockchaininfo | jq '.')
done