FROM python:3.6

# Install useful packages
RUN apt-get -y update && apt-get -y install vim postgresql-client

# Do everything relative to /usr/src/app which is where we install our
# application.
WORKDIR /usr/src/app

# Install any explicit requirements
ADD requirements/*.txt ./requirements/
RUN pip install -r ./requirements/developer.txt

# The IAR Stats Gatherer source will be mounted here as a volume
VOLUME /usr/src/app

# Copy startup script
ADD ./compose/start.sh ./compose/wait-for-it.sh /tmp/

# By default, use the Django development server to serve the application and use
# developer-specific settings.
#
# *DO NOT DEPLOY THIS TO PRODUCTION*
ENV DJANGO_SETTINGS_MODULE gatherstats_project.settings_developer
ENTRYPOINT ["/tmp/wait-for-it.sh", "iar-gatherstats-db:5432", "--"]
CMD ["/tmp/start.sh"]
