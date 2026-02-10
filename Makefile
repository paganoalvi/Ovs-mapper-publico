help:
	@echo "———————————————————————————————"
	@echo " Usage: make [options]"
	@echo " Options:"
	@echo "  help:  show this help message"
	@echo "  graph: generate graph"
	@echo "  clean: clean up the project"
	@echo "———————————————————————————————"

graph:
	.venv/bin/python csv2pronto -s ./input/input.csv -d ./output/out.ttl -f ttl -o ./ontology/pronto.owl -ss "argenprop=site1,mercadolibre=site2,zonaprop=site3" --input_source scraper

	# Whit .venv activated:
	python3 csv2pronto -s ./input/input_scraper_prueba.csv -d ./output/out.ttl -f ttl -o ./ontology/inmontology_v2.owl -ss "argenprop=site1,mercadolibre=site2,zonaprop=site3" --input_source scraper

clean:
	find . -name "__pycache__" -exec rm -fr {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	rm -f ./output/out.ttl 
