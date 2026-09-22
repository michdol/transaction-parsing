The initial prompt is in instructions/AGENTS.md

1. One extra step I did was to add Dockerimage for the frontend. I like to keep frontend containerised.
2. Created basic frontend app. No additional instructions here.
3. Created backend starting with ImportService to be injected into FastApi app.
4. Refactored the service to implement a TabularReader protocol to allow extending the app for different input files in the future (excel for example).
5. Refactored validation into validators classes to be injected into import service. If validation rules for header change, the validator class changes, but consuming service is not impacted.

Architectural style: would use layered architecture for FastApi:
- presentation layer: FastApi
- service layer: ImportService
- persistence layer: TransactionRepository - this was skipped

This approach allows for structuring the app along with dependency injection (would use dependency_injector package)
which allows for decoupling the components and simplifies unit and integration tests by allowing to use fakes.

Things ommitted:
- automated tests, the biggest one and first step to introduce in the real project
    - would be time consuming and generated React allowed for quick manual tests that were sufficient
- pydantic models for Http requests and responses
- logging
- transaction repository - to complete the layered architecture style of the app



Instructions to run:

Backend:

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
fastapi run backend/main.py
```

Frontend:

```sh
cd frontend
docker build -t front .
docker run -p 5173:5173 -t front
```

Altough npm commands for running frontend from README.md might work, I use docker.
