help:
	@echo "———————————————————————————————"
	@echo " Usage: make [options]"
	@echo " Options:"
	@echo "  help:  show this help message"
	@echo "  graph: generate graph"
	@echo "  clean: clean up the project"
	@echo "———————————————————————————————"

graph:
	# ojo que la version nueva es inmontology_v2.owl y aca se esta usando pronto.owl
	.venv/bin/python csv2pronto -s ./input/input.csv -d ./output/out.ttl -f ttl -o ./ontology/pronto.owl -ss "argenprop=site1,mercadolibre=site2,zonaprop=site3" --input_source scraper

	# con el .venv activado:
	python3 csv2pronto -s ./input/input.csv -d ./output/out.ttl -f ttl -o ./ontology/inmontology_v2.owl -ss "argenprop=site1,mercadolibre=site2,zonaprop=site3" --input_source scraper

clean:
	find . -name "__pycache__" -exec rm -fr {} +
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	rm -f ./out.ttl
