build:
	docker build -t irnet .

run:
	docker stop /irnet || echo ok
	docker rm /irnet || echo ok
	mkdir -p cache
	docker run --name /irnet -v "$(PWD)/cache:/cache:delegated" -p 5050:5050 -dit irnet # /bin/bash

exec:
	docker exec -it /irnet /bin/bash
