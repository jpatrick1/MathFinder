FROM ubuntu:16.04 AS builder

RUN \
mkdir -p /usr/share/man/man1 && \
export BUILD_PKGS="autoconf automake build-essential libtool git" && \
export PKGS="python3-pip python3-setuptools libleptonica-dev libpng-dev libqt4-dev libjpeg-turbo8-dev openjdk-8-jdk xzgv libcanberra-gtk-module" && \
export DEBIAN_FRONTEND=noninteractive && \
apt-get -qq update && \
apt-get -qq -y --no-install-recommends install $BUILD_PKGS $PKGS && \
ln -s /usr/bin/python3.5 /usr/bin/python

COPY . /MathFinder
RUN \
cd /MathFinder/ && \
autoreconf -vfi && \
./configure && \
make -j4 && make install && \
cp -R /MathFinder/training /usr/local/ && \
cd /MathFinder/server && \
pip3 install .

FROM ubuntu:16.04
COPY --from=builder /usr/local/ /usr/local/

RUN \
export PKGS="python3.5 python3-setuptools liblept5 libpng16-16 qt4-default libjpeg-turbo8 openjdk-8-jdk xzgv libcanberra-gtk-module" && \
export DEBIAN_FRONTEND=noninteractive && \
apt-get -qq update && \
apt-get -qq -y --no-install-recommends install $PKGS && \
rm -rf /var/lib/apt/lists/* && \
ln -s /usr/bin/python3.5 /usr/bin/python && \
chmod -R 777 /usr/local/training && \
mkdir -p /.mathfinder && \
mkdir -p /root/.mathfinder && \
ln -s /usr/local/training /.mathfinder/ && \
ln -s /usr/local/training /root/.mathfinder/

EXPOSE 9030
