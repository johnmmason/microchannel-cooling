IMAGE=sd-api:0.1

stop :
	docker kill sd-api

run : build
	docker run -d --rm -p 5000:5000 --name sd-api ${IMAGE}

build : Dockerfile api.py model
	docker build -t ${IMAGE} .
