SELECT
	driver.driver_id,
	run.run_id,
	score.score,
	score.timestamp,
	1 / road_characteristic.curvature as radius
FROM
	driver
	JOIN run ON driver.driver_id = run.driver_id
	JOIN score on run.run_id = score.run_id
	JOIN road_characteristic ON run.run_id = road_characteristic.run_id
	AND score.timestamp = road_characteristic.timestamp;
