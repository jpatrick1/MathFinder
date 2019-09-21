FROM ubuntu:16.04 AS builder

RUN \
mkdir -p /usr/share/man/man1 && \
export BUILD_PKGS="autoconf automake build-essential libtool git" && \
export PKGS="libpng-dev libqt4-dev libjpeg-turbo8-dev openjdk-8-jdk xzgv libcanberra-gtk-module" && \
export DEBIAN_FRONTEND=noninteractive && \
apt-get -qq update && \
apt-get -qq -y --no-install-recommends install $BUILD_PKGS $PKGS

COPY . /MathFinder

RUN \
cd /MathFinder/src/THIRDPARTY/leptonica-1.73 && \
aclocal && \
autoreconf -vfi && \
./configure && \
make -j4 && make install && \
cd /MathFinder/ && \
autoreconf -vfi && \
./configure && \
make -j4 && make install

FROM ubuntu:16.04
COPY --from=builder /usr/local/ /usr/local/

RUN \
export PKGS="libpng16-16 qt4-default libjpeg-turbo8 openjdk-8-jdk xzgv libcanberra-gtk-module" && \
export DEBIAN_FRONTEND=noninteractive && \
apt-get -qq update && \
apt-get -qq -y --no-install-recommends install $PKGS && \
rm -rf /var/lib/apt/lists/*
