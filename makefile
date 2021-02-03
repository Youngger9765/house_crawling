.PHONY:

test_leju:
	serverless invoke local -f leju

run_leju_in_github:
	python3 leju.crawl()