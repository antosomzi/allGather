init-db-cluster:
	initdb -D /home/gpu_user/hho48/postgresql

start-db-server:
	pg_ctl -D '/opt/homebrew/var/postgres@15' -l logfile start

run:
	uvicorn driver_score.app:app --reload

sqlacodegen:
	sqlacodegen postgresql://gpu_user:@localhost:5432/gpu_user > driver_score/db/models.py

freeze:
	pip freeze > requirements/prod.txt

# curl:
# 	curl -X POST -F "file=@/home/gpu_user/hho48/DriverScore_backend/data/2022_05_25_20_19_06_302.zip" http://127.0.0.1:8000/api/v1/allgather/upload
# 	curl -X POST -F "file=@/home/gpu_user/hho48/DriverScore_backend/data/2022_10_20_17_46_13_503.zip" http://127.0.0.1:8000/api/v1/allgather/upload
# 	curl -X POST -F "file=@/home/gpu_user/hho48/DriverScore_backend/data/2023_05_26_18_27_47_621.zip" http://127.0.0.1:8000/api/v1/allgather/upload
# 	curl -X POST -F "file=@/home/gpu_user/hho48/DriverScore_backend/data/2022_05_25_21_26_53_109.zip" http://127.0.0.1:8000/api/v1/allgather/upload
# 	curl -X POST -F "file=@/home/gpu_user/hho48/DriverScore_backend/data/peyton.zip" http://127.0.0.1:8000/api/v1/allgather/upload

upload-route:
	curl -X POST -F "file=@/home/gpu_user/hho48/DriverScore_backend/data/SR11.zip" http://127.0.0.1:8000/api/v1/routes/upload
	curl -X POST -F "file=@/home/gpu_user/hho48/DriverScore_backend/data/SR11_curves.geojson" http://127.0.0.1:8000/api/v1/routes/curves/upload

upload-curve:
	curl -X POST -F "file=@/home/gpu_user/hho48/DriverScore_backend/data/SR190_curves.geojson" http://127.0.0.1:8000/api/v1/routes/curves/upload

FILES := \
  /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_15_20_21_830.zip\
    /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_15_39_51_751.zip\
	  /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_16_44_37_164.zip\
	    /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_17_48_38_211.zip\
 /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_15_28_19_811.zip\
   /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_16_42_27_573.zip\
     /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_17_44_24_761.zip\
	   /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_17_48_38_593.zip\
 /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_15_28_19_914.zip\
   /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_16_44_34_787.zip\
     /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_17_48_20_110.zip\
	   /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_17_48_40_520.zip

URL := http://127.0.0.1:8000/api/v1/allgather/upload

upload-allgather:
	@for file in $(FILES); do \
		echo "Uploading $$file..."; \
		curl -X POST -F "file=@$$file" $(URL); \
		echo ""; \
	done
