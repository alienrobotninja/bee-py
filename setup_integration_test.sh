#!/bin/bash

bee-factory start --detach 1.9.0

# BEE_POSTAGE
bee_postage=$(echo "Y" | swarm-cli stamp buy --bee-api-url http://localhost:1633/ --depth 23 --amount 100000000000 | grep "Stamp ID" | cut -d ' ' -f3)

# BEE_PEER_POSTAGE
bee_peer_postage=$(echo "Y" | swarm-cli stamp buy --bee-api-url http://localhost:11633/ --depth 23 --amount 100000000000 | grep "Stamp ID" | cut -d ' ' -f3)

echo "BEE_POSTAGE: $bee_posage"
echo "BEE_PEER_POSTAGE: $bee_peer_posage"