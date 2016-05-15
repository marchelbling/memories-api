FROM python:2.7.9

RUN apt-get -y update --fix-missing && apt-get install -y \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev

ADD . /api
RUN pip install -r /api/requirements.txt \
 && chmod a+x /api/memories/run.sh

EXPOSE 8000
CMD ["/api/memories/run.sh"]
