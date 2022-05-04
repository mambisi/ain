#!/bin/bash
block_n=$(./src/defi-cli getblockchaininfo | jq '.blocks' )
echo $block_n
echo $(./src/defi-cli getblockchaininfo | jq '.' )
# Sync node to 100000 blocks
while [ "$block_n" -lt 100000 ] 
do
    sleep 1
    echo $(./src/defi-cli getblockchaininfo | jq '.')
done