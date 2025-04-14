# NH Facts AI  

Inspired by: https://fastapi.tiangolo.com/project-generation/

### Technologies used:  
- FastAPI
- Python 3.13
- Conda (https://docs.anaconda.com/miniconda/)
- Postgres (brew install postgresql)


### Setup Your Environment:

```bash
conda create -n "education-backend" python=3.13
conda activate education-backend
cd backend
pip install -r requirements.txt
```

### Updating requirements.txt

```bash
pip freeze > requirements.txt
```

```bash
docker-compose build
docker-compose up
# if you want to run with realtime file changes
docker-compose watch
```

### Running db migrations: 
```bash
PYTHONPATH=. alembic upgrade head # Don't know why there is a path issue.
```

### Creating a new migration: 
```bash
PYTHONPATH=. alembic revision --autogenerate -m "migration_name"
```

### Dev Run
```bash 
uvicorn app.main:app --reload --ssl-keyfile=./certs/key.pem --ssl-certfile=./certs/cert.pem
```

### If you want to crete new certs:
```bash
cd backend
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365
fastapi dev app/main.py --ssl-keyfile=./certs/key.pem --ssl-certfile=./certs/cert.pem
```

### Refreshing Docker
```bash
docker-compose down -v
docker-compose watch
```

### Debug configuration with VSCode
```json
{
    // Use IntelliSense to learn about possible attributes.
    // Hover to view descriptions of existing attributes.
    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Attach (remote debug)",
            "type": "debugpy",
            "request": "attach",
            "connect": {
                "host": "127.0.0.1",
                "port": 5678
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}/backend",
                    "remoteRoot": "/app"
                }
            ]
        },
    ]
}
```

### Production Deployment

[Review Deployment.md](Deployment.md)

### Key Python Libs: 
- **psycopg** - Connect to Postgres  
- **pydantic-settings** - Load settings from .env file
- **bcrypt** - Hash passwords
- **passlib** - Password validation
- **pyjwt** - Create JWTs
- **sqlmodel** - ORM for Postgres
- **fastapi[standard]** - Web Framework
- **alembic** - Database migrations
- **pip** - should switch to uv at some point.

## TODO: 
- Add traefik as our reverse proxy. Ensure we setup proper LB.  Ensure we setup HTTPS.  Ideally use K8's.  
- Update to use uv.
- Updates to ensure CORS is setup properly. 
- Review this: https://github.com/zhanymkanov/fastapi-best-practices
- Add background tasks. 
- Add Apache Kafka
- Validate if this is a good idea: pip install --only-binary :all: tokenizers.  Needed for anthropic.