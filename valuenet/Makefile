build:
	docker build -t valuenet .

run:
	docker stop /valuenet || echo ok
	docker rm /valuenet || echo ok
	docker run --name /valuenet -v "$(PWD)/../cache:/cache:delegated" -p 5050:5050 -dit valuenet

exec:
	docker exec -it /valuenet /bin/bash
