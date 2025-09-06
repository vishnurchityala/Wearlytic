.PHONY: test-scraping-agent

-include .env
export $(shell sed 's/=.*//' .env)

test-scraping-agent:
	@echo "<========== Validating ScrapingAgent Service ==========>"
	@curl -fs ${SCRAPING_AGENT_API_URL} > /dev/null \
		&& echo "<=========== ScrapingAgent Service is Started ===========>" \
		|| (echo "<=========== ScrapingAgent is NOT running! =========>" && exit 1)

run: test-scraping-agent
	@echo "<========== Starting Data Ingestor Service ===========>"
	@echo "<========== Started Data Ingestor Service ===========>"
