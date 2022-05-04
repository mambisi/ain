from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException

# rpc_user and rpc_password are set in the bitcoin.conf file
rpc_connection = AuthServiceProxy("http://0.0.0.0:8332")
getblockchaininfo = rpc_connection.getblockchaininfo()
print(getblockchaininfo)