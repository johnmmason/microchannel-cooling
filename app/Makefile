NAME=sd-api
version=0.1
PORT=5000
IMAGE=$(NAME):$(version)

stop :
	- docker kill ${NAME}

build :
	docker build -t ${IMAGE} .

run : build
	docker run -dit --rm -p $(PORT):$(PORT) --name ${NAME} ${IMAGE}

sleep :
	sleep 1

test :
	./example_post.sh

clean:
	- docker rmi -f ${IMAGE}
	- docker rm /${NAME}

iterate: stop clean run sleep test