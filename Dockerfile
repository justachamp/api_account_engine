FROM python:3.6-slim

LABEL version="0.0.1" \
      company="Cumplo" \
      project="The Kimchi Project"


RUN useradd -ms /bin/bash kimchi

COPY --chown=kimchi:kimchi requirements.txt /home/kimchi/requirements.txt

RUN apt-get -qq update \
	&& apt-get -qq install default-libmysqlclient-dev python3-mysqldb python-dev build-essential -y --no-install-recommends \
	&& pip install -r /home/kimchi/requirements.txt --upgrade -q \
	&& apt-get -qq remove default-libmysqlclient-dev python3-mysqldb build-essential python-dev -y \
    && rm -rf /root/.cache \
    && rm -rf /var/lib/apt/lists/*


USER kimchi
COPY --chown=kimchi:kimchi . /home/kimchi
WORKDIR /home/kimchi


ENV DJANGO_DEBUG False
ENV SECRET_KEY 'se-$d6$#gfumn0qhj)m)rh-3z=d&4t4s=+cn*o@*w%q78*a!53'
ENV CORS_ORIGIN_ALLOW_ALL True
ENV ALLOWED_HOSTS '*'
ENV LOGS_DIR 'logs'
ENV MANDRILL_API_KEY 'mandrill key'
ENV OAUTH_GOOGLE_KEY 'your key here'
ENV OAUTH_GOOGLE_SECRET 'your secret here'


RUN	python manage.py collectstatic --noinput 

COPY --chown=kimchi:kimchi ./docker-entrypoint.sh  /home/kimchi/docker-entrypoint.sh

EXPOSE 8001

ENTRYPOINT ["/home/kimchi/docker-entrypoint.sh"]
CMD ["uwsgi", "uwsgi.ini"]


