.PHONY: images models

all: clean images models

clean: clean-models clean-images
	rm -rf .nv .cache .local
	rm -rf models/.nv
	
clean-images:
	rm -f images/cloudmesh*.sif

clean-models:
	rm -rf modesl/large_tcnn
	rm -rf models/medium_cnn
	rm -rf models/small_lstm
	rm -rf __pycache__

images:
	sh images.sh

models:
	sh create-models.sh
	sh check-models.sh
