Extension of [MathFinder](https://github.com/jrbruce86/MathFinder) by creating a simple interface and using in Docker (Ubuntu:16.04)

## Installation
see Dockerfile

## Usage
Need to run as host user so GUI apps work.  
`docker-compose run --user=$(id -u):$(id -g) MathFinder`

```bash
# inside running container
MathFinder -m
```
