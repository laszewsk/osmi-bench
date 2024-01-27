ijob -c 6  \
            --gres=gpu:a100:1 \
            --time=3:00:00 \
            --reservation=bi_fox_dgx \
            --partition=bii-gpu \
            --account=bii_dsc_community \
            --mem=256G 

# For medium and small we only need 64GB

