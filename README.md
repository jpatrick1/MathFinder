Extension of [MathFinder](https://github.com/jrbruce86/MathFinder) by creating a simple interface and using in Docker (Ubuntu:16.04)

## Installation
see Dockerfile

## Usage
Need to run as host user so GUI apps work.  
`USER_ID=$(id -u):$(id -g) docker-compose run -p 9030:9030 MathFinder`

`USER_ID=$(id -u):$(id -g) docker-compose up -d`

```bash
# inside running container
MathFinder -m
```

## HTTP Server w/Swagger Interface
Run docker-compose w/entrypoint `python -m mathfinder.server`  

Swagger interface: http://localhost:9030/api/v1/ui
