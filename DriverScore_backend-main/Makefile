# PostgreSQL configuration
PG_USER := $(shell whoami)  # Utilise l'utilisateur système par défaut
PG_DB := gpu_user
PG_DATA_DIR := /opt/homebrew/var/postgresql@14

# Check database user and connection
check-pg-path:
	@echo "Using PostgreSQL data directory: $(PG_DATA_DIR)"
	@if [ ! -d "$(PG_DATA_DIR)" ]; then \
		echo "ERROR: PostgreSQL data directory not found at: $(PG_DATA_DIR)"; \
		exit 1; \
	else \
		echo "✓ Directory exists"; \
	fi

check-user: check-pg-path
	@echo "Current PostgreSQL user:"
	@psql -c "SELECT current_user, current_database();" || echo "Cannot connect to PostgreSQL. Is the server running?"

# Start PostgreSQL server with better error handling
start-db: check-pg-path
	@echo "Starting PostgreSQL server as PostgreSQL user '$(PG_USER)'..."
	@if pg_ctl status -D "$(PG_DATA_DIR)" > /dev/null 2>&1; then \
		echo "✓ PostgreSQL server is already running"; \
	else \
		pg_ctl -D "$(PG_DATA_DIR)" -l logfile start && \
		echo "✓ PostgreSQL server started successfully"; \
	fi
	@echo "PostgreSQL server is running with system user: $(shell whoami)"
	@echo "To check the actual PostgreSQL user, run: make check-user"

# Check if database exists
check-db-exists: start-db
	@if psql -U $(PG_USER) -d postgres -lqt | cut -d \| -f 1 | grep -qw $(PG_DB); then \
		echo "✓ Database '$(PG_DB)' already exists"; \
		return 0; \
	else \
		echo "Database '$(PG_DB)' does not exist yet"; \
		return 1; \
	fi

# Database setup command
setup-db: start-db
	@echo "Setting up database as user '$(PG_USER)'..."
	@echo "Checking if database exists..."
	@if psql -U $(PG_USER) -d postgres -lqt | cut -d \| -f 1 | grep -qw $(PG_DB); then \
		echo "✓ Database '$(PG_DB)' already exists"; \
	else \
		echo "Creating database '$(PG_DB)'..."; \
		createdb -U $(PG_USER) $(PG_DB); \
		echo "✓ Database created"; \
	fi
	@echo "Enabling PostGIS extension..."
	@psql -U $(PG_USER) -d $(PG_DB) -c "CREATE EXTENSION IF NOT EXISTS postgis;"
	@echo "Applying all migrations..."
	@poetry run alembic upgrade head
	@echo "Database setup complete!"



run:
	uvicorn driver_score.app:app --reload

freeze:
	pip freeze > requirements/prod.txt

# curl:
# 	curl -X POST -F "file=@/home/gpu_user/hho48/DriverScore_backend/data/2022_05_25_20_19_06_302.zip" http://127.0.0.1:8000/api/v1/allgather/upload
# 	curl -X POST -F "file=@/home/gpu_user/hho48/DriverScore_backend/data/2022_10_20_17_46_13_503.zip" http://127.0.0.1:8000/api/v1/allgather/upload
# 	curl -X POST -F "file=@/home/gpu_user/hho48/DriverScore_backend/data/2023_05_26_18_27_47_621.zip" http://127.0.0.1:8000/api/v1/allgather/upload
# 	curl -X POST -F "file=@/home/gpu_user/hho48/DriverScore_backend/data/2022_05_25_21_26_53_109.zip" http://127.0.0.1:8000/api/v1/allgather/upload
# 	curl -X POST -F "file=@/home/gpu_user/hho48/DriverScore_backend/data/peyton.zip" http://127.0.0.1:8000/api/v1/allgather/upload

# upload-route:
# 	curl -X POST -F "file=@/home/gpu_user/hho48/DriverScore_backend/data/SR11.zip" http://127.0.0.1:8000/api/v1/routes/upload
# 	curl -X POST -F "file=@/home/gpu_user/hho48/DriverScore_backend/data/SR11_curves.geojson" http://127.0.0.1:8000/api/v1/routes/curves/upload

# upload-curve:
# 	curl -X POST -F "file=@/home/gpu_user/hho48/DriverScore_backend/data/SR190_curves.geojson" http://127.0.0.1:8000/api/v1/routes/curves/upload

# FILES := \
#   /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_15_20_21_830.zip\
#     /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_15_39_51_751.zip\
# 	  /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_16_44_37_164.zip\
# 	    /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_17_48_38_211.zip\
#  /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_15_28_19_811.zip\
#    /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_16_42_27_573.zip\
#      /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_17_44_24_761.zip\
# 	   /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_17_48_38_593.zip\
#  /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_15_28_19_914.zip\
#    /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_16_44_34_787.zip\
#      /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_17_48_20_110.zip\
# 	   /home/gpu_user/hho48/DriverScore_backend/data/Vogel_2024/2024_05_09_17_48_40_520.zip

# URL := http://127.0.0.1:8000/api/v1/allgather/upload

# upload-allgather:
# 	@for file in $(FILES); do \
# 		echo "Uploading $$file..."; \
# 		curl -X POST -F "file=@$$file" $(URL); \
# 		echo ""; \
# 	done
