FROM python:2.7.9

ADD . /api
RUN chmod a+x /api/memories/run.sh
EXPOSE 8000
CMD ["/api/memories/run.sh"]
