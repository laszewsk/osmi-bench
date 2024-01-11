ijob -c 4  \
            --gres=gpu:v100:1 \
            --time=3:00:00 \
            --partition=bii-gpu \
            --account=bii_dsc_community \
            --mem=256G 

# For medium and small we only need 64GB

