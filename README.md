Extension of [MathFinder](https://github.com/jrbruce86/MathFinder) by creating a simple interface and using in Docker (Ubuntu:16.04)

## MathFinder Installation
see [Dockerfile](https://github.com/jpatrick1/MathFinder/blob/docker/Dockerfile)

## Usage
### Docker
`docker pull jpatrick1/mathfinder`

[docker-compose](https://github.com/jpatrick1/MathFinder/blob/docker/docker-compose.yml)

Need to run as host user so GUI apps work.  
```bash
USER_ID=$(id -u):$(id -g) docker-compose run -p 9030:9030 MathFinder
USER_ID=$(id -u):$(id -g) docker-compose up -d
```

```bash
# inside running container
MathFinder -m
```

## HTTP Server w/Swagger Interface
Run docker-compose w/entrypoint `python -m mathfinder.server`  

Swagger interface: http://localhost:9030/api/v1/ui

