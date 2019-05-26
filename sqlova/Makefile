default:
	docker build -t paulfitz/sqlova .

start:
	docker run --name sqlova \
		-v "$(PWD):/share" \
		-dit paulfitz/sqlova

stop:
	docker stop sqlova || echo ok
	docker kill sqlova || echo ok
	docker rm sqlova

inspect:
	docker exec -it sqlova /bin/bash
