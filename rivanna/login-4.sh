ijob -c 1  \
            --gres=gpu:a100:4 \
            --time=3:00:00 \
            --reservation=bi_fox_dgx \
            --partition=bii-gpu \
            --account=bii_dsc_community
