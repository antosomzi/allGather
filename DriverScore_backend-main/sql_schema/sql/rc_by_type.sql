SELECT
	driver.driver_id, score.score
FROM
	driver
	JOIN run ON run.driver_id = driver.driver_id
	JOIN score ON run.run_id = score.run_id;
