#!/bin/bash
block=0
attempts=0
# Sync node to 10000 blocks
while [ "$block" -lt 10000 ] 
do
    sleep 5
    b=$(./src/defi-cli getblockchaininfo | jq '.blocks' )
    block=$${b:-$block}
    echo "===> Block Height $block"
    if [ $attempts -gt 12 ]; then
        echo "Failed to bootstrap after a minute."
        exit 1
    fi
    attempts=$(($attempts + 1))
done