.PHONY: images models

all: clean images models

clean: clean-models clean-images

clean-images:
	rm -f images/cloudmesh*.sif

clean-models:
	rm -rf modesl/large_tcnn
	rm -rf models/medium_cnn
	rm -rf models/small_lstm

images:
	sh images-2.sh

models:
	sh create-models.sh
	sh check-models.sh
