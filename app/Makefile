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

debug : build
	docker run -it --rm -p $(PORT):$(PORT) --name ${NAME} ${IMAGE}

sleep :
	sleep 1

test :
	./example_post.sh

clean:
	- docker rmi -f ${IMAGE}
	- docker rm /${NAME}
	- docker images --quiet --filter=dangling=true | xargs --no-run-if-empty docker rmi
	# dangling image cleanup

purge: clean
	- docker system prune -a -f

run_tests: stop clean run sleep test
iterate: stop clean debug