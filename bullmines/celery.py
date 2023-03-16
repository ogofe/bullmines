from celery import Celery, shared_task
from bitcoinrpc.authproxy import AuthServiceProxy

# Celery Setup
app = Celery('')

# Bitcoin node connection information
rpc_user = "your_rpc_username"
rpc_password = "your_rpc_password"
rpc_port = 8332  # or the port number of your Bitcoin node
rpc_url = f"http://{rpc_user}:{rpc_password}@localhost:{rpc_port}/"

# Wallet address to monitor for incoming transactions
watch_address = "your_watch_address"

# Set up a connection to the Bitcoin node over JSON-RPC
bitcoin_rpc = AuthServiceProxy(rpc_url)

@shared_task
def monitor_bitcoin_transactions():
    # Set up a notification for incoming transactions involving the watch address
    bitcoin_rpc.importaddress(watch_address, "", False)
    bitcoin_rpc.zmq("pubhashblock", "tcp://127.0.0.1:28332")
    bitcoin_rpc.zmq("pubhashtx", f"tcp://127.0.0.1:28333", watch_address)

    # Wait for incoming transactions
    while True:
        try:
            message = bitcoin_rpc.zmq("sub", f"tcp://127.0.0.1:28333")
            if message["address"] == watch_address:
                # Push a message to a Django Channels WebSocket group
                async_to_sync(channel_layer.group_send)(
                    "bitcoin_updates",
                    {
                        "type": "bitcoin.update",
                        "message": {
                            "txid": message["txid"],
                            "amount": message["vout"][0]["value"],
                            "confirmations": message["confirmations"],
                        },
                    },
                )
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
