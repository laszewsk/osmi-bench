
#!/bin/sh
cd benchmark
python3 tfs_grpc_client.py -m medium_cnn -b 32 -n 10 localhost:8500
