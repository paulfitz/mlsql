start:
	docker run --name sqlova -d -p "5050:5050" paulfitz/sqlova

build:
	./fetch_models.sh
	docker build -t paulfitz/sqlova .

stop:
	docker stop sqlova || echo ok
	docker kill sqlova || echo ok
	docker rm sqlova
