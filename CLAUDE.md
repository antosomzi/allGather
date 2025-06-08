# DriverScore Monorepo - Claude Reference Documentation

## Project Overview
DriverScore is a monorepo containing a driving analytics platform with geospatial data processing capabilities. It includes a Python FastAPI backend and a React TypeScript frontend for analyzing driver behavior using smartphone sensor data.

## Repository Structure
```
DriverScore_backend-main/     # Python FastAPI backend
DriverScore_frontend-main/    # React TypeScript frontend
```

---

## Backend Architecture (`DriverScore_backend-main/`)

### Technology Stack
- **FastAPI 0.103.0** - Modern async web framework
- **Python 3.10** - Required (cannot use 3.12 due to sqlacodegen conflict)
- **SQLAlchemy 1.4.52** - ORM with declarative base pattern
- **PostgreSQL + PostGIS** - Spatial database with GeoAlchemy2
- **Alembic** - Database migrations
- **Poetry** - Dependency management

### Key Dependencies
- **Geospatial**: GeoPandas, Shapely, PyProj, Fiona, GeoAlchemy2
- **Data Processing**: NumPy, Pandas
- **Development**: Ruff (linting), MyPy (typing), Pytest

### Application Structure
```
driver_score/
├── main.py              # Simple FastAPI setup
├── app.py              # Enhanced app with CORS/ORJSON
├── settings.py         # Dynaconf configuration
├── core/               # Infrastructure
│   ├── database.py     # Session management
│   └── models.py       # SQLAlchemy ORM models
└── domains/            # Domain-driven design
    ├── allgather/      # Mobile data ingestion
    ├── driver/         # Driver management
    ├── model/          # Scoring algorithms
    ├── route/          # Road infrastructure
    ├── run/            # Driving sessions
    └── summary/        # Analytics & reporting
```

### Domain Architecture

#### 1. AllGather Domain (`/api/v1/allgather`)
- **Purpose**: Mobile app data ingestion
- **Features**: File upload (.zip/.tar), GPS/IMU processing, coordinate transformation
- **Key Service**: `AllGatherService` with data extraction and validation

#### 2. Driver Domain (`/api/v1/drivers`)
- **Purpose**: Driver management and run history
- **Features**: Driver CRUD, run associations

#### 3. Run Domain (`/api/v1/runs`)
- **Purpose**: Driving session management
- **Features**: Run CRUD, GPS/IMU sample retrieval, driver scores by direction

#### 4. Route Domain (`/api/v1/routes`)
- **Purpose**: Road infrastructure analysis
- **Features**: Route geometry upload, curve inventory, road characteristics calculation

#### 5. Model Domain (`/api/v1/model`)
- **Purpose**: Driver scoring algorithms
- **Features**: Sliding window-based scoring (default: 10 samples), GPS/IMU analysis

#### 6. Summary Domain (`/api/v1/summary`)
- **Purpose**: Aggregated analytics
- **Features**: Pivot tables by road characteristic ranges/types

### Database Models
- **Core**: Driver, Run, DissolvedRoute, CurveInventory
- **Sensor Data**: GpsSample, ImuSample (composite keys: run_id, timestamp)
- **Derived**: RoadCharacteristic, Score
- **Audit**: UploadLog, CollectedDataFile
- **Spatial**: PostGIS with 3D geometry support (LINESTRINGZ, POINT)

### Configuration
- **Settings**: YAML-based with Dynaconf (`configs/settings.yaml`)
- **Environment**: Dev/prod environment support
- **Database**: PostgreSQL connection strings
- **CORS**: Wildcard origins (development)

### Development Commands
```bash
# Database setup and migration
make setup-db          # Setup PostgreSQL database
make run-migrations    # Run Alembic migrations
make run-server        # Start uvicorn server

# Development
poetry install         # Install dependencies
poetry shell          # Activate virtual environment
```

---

## Frontend Architecture (`DriverScore_frontend-main/`)

### Technology Stack
- **React 18** with TypeScript
- **Vite** - Build tool and dev server
- **TanStack Router** - File-based routing with type safety
- **TanStack Query** - Server state management
- **Chakra UI** - Component library and design system
- **Leaflet & React-Leaflet** - Interactive maps

### Key Dependencies
- **Visualization**: Recharts, Syncfusion Pivot View
- **Forms**: Formik, React Hook Form
- **Animation**: Framer Motion
- **Utils**: Lodash, Immer
- **HTTP**: Axios (via generated client)

### Application Structure
```
src/
├── routes/             # File-based routing
│   ├── __root.tsx      # Root layout
│   ├── _layout.tsx     # Protected layout
│   ├── _layout/        # Protected routes
│   │   ├── index.tsx   # Dashboard
│   │   ├── Map.tsx     # Map visualization
│   │   └── FileUpload.tsx # Data upload
│   └── login.tsx       # Authentication
├── components/Common/  # Shared UI components
├── features/Map/       # Feature-based organization
├── client/            # Generated API client
├── hooks/             # Custom React hooks
└── config.json        # Configuration
```

### Features Architecture - Map Feature
```
features/Map/
├── components/         # Map-specific components
│   ├── DrivingSession.tsx      # Main map overlay
│   ├── CustomPolyline.tsx      # Styled trajectories
│   ├── SampleChart.tsx         # Interactive charts
│   ├── DriverSessionModal.tsx  # Session selection
│   └── Trajectory.tsx          # GPS visualization
├── enums/             # Constants and display options
├── types/             # TypeScript definitions
└── utils/             # Map calculations and processing
```

### API Client Generation
- **OpenAPI Code Generation**: Automated from backend OpenAPI spec
- **Generated Services**: AllGatherService, RunsService, RoutesService, etc.
- **Type Safety**: Full TypeScript models and schemas
- **Custom Script**: `modify-openapi-operationids.js` for operation ID cleanup

### State Management
- **Server State**: TanStack Query with query keys like `["scores", fetchRunIds]`
- **Local State**: React useState for component state
- **No Global State**: URL state and server state synchronization
- **TODO**: Replace prop drilling with Zustand

### Development Commands
```bash
npm install           # Install dependencies
npm run dev          # Start development server
npm run build        # Production build
npm run preview      # Preview production build
npm run generate     # Generate API client from OpenAPI spec
```

---

## Key Architectural Patterns

### Backend Patterns
1. **Domain-Driven Design**: Clear domain boundaries with dedicated services
2. **Service Layer Pattern**: Business logic encapsulation
3. **Dependency Injection**: Database sessions via FastAPI dependencies
4. **Spatial Data Processing**: PostGIS integration with GeoPandas
5. **Async-First**: FastAPI with proper async/await patterns

### Frontend Patterns
1. **Feature-Based Organization**: Self-contained feature modules
2. **Type-Safe Development**: Comprehensive TypeScript with generated types
3. **Query-Driven Data Fetching**: TanStack Query for server state
4. **Component Composition**: Chakra UI with custom theme
5. **Code Generation**: Automated API client from OpenAPI spec

---

## Data Flow Architecture

### Mobile Data Processing Pipeline
1. **Mobile App Upload** → AllGather domain receives compressed files
2. **Data Extraction** → Python-magic validation and file processing
3. **GPS/IMU Processing** → Coordinate transformation and sample validation
4. **Scoring Algorithm** → Sliding window analysis with road context
5. **Frontend Visualization** → Real-time map updates with synchronized charts

### API Communication
- **Backend**: OpenAPI 3.0 specification with versioned endpoints
- **Frontend**: Generated TypeScript client with type-safe services
- **Authentication**: Token-based (currently mocked in frontend)

---

## Current TODOs and Limitations

### Backend
- [ ] Enhance testing coverage (minimal pytest implementation)
- [ ] Implement comprehensive error handling
- [ ] Security hardening (remove wildcard CORS)
- [ ] Add monitoring and observability
- [ ] Improve API documentation

### Frontend
- [ ] Implement real authentication (currently mocked)
- [ ] Replace prop drilling with Zustand state management
- [ ] Add comprehensive error boundaries
- [ ] Implement testing framework
- [ ] Enhance client-side validation

---

## Development Workflow

### Database Setup
1. Install PostgreSQL with PostGIS extension
2. Run `make setup-db` to create database and user
3. Run `make run-migrations` to apply schema
4. Use `make run-server` to start backend

### Frontend Development
1. Ensure backend is running on configured API URL
2. Run `npm run generate` to update API client
3. Use `npm run dev` for hot-reload development
4. Charts and map synchronization works out of the box

### Full Stack Development
- Backend runs on port 8000 (configurable)
- Frontend runs on port 5173 (Vite default)
- CORS configured for local development
- API client auto-generates from backend OpenAPI spec

---

## Production Considerations

### Backend Deployment
- Multi-stage Dockerfile with Poetry
- Uvicorn-Gunicorn for production ASGI server
- PostgreSQL with PostGIS required
- Environment-specific configuration via Dynaconf

### Frontend Deployment
- Static build output via Vite
- Environment variables for API URL configuration
- Syncfusion license key required for pivot tables
- Map tiles require Leaflet configuration

This documentation serves as a comprehensive reference for understanding and working with the DriverScore monorepo architecture.