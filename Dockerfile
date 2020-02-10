FROM python:3.8.1


ENV DIRECTORY /arscca-pyramid

# Set timezone so python will correctly interpret datetime.datetime.now()
ENV TZ 'America/Chicago'

WORKDIR ${DIRECTORY}

# Copy the files required in order to install dependencies
# Note we are copying them to the same directory where
# we will later bind-mount the whole repository.
# The reason we use the same location is so that python
# knows where the ${DIRECTORY_NAME} package is.

# Required in order to pip install
COPY requirements.txt .

# Required in order to pip install the testing requirements
# https://docs.pylonsproject.org/projects/pyramid/en/1.7-branch/tutorials/wiki/installation.html#install-testing-requirements
COPY setup.py .

# Why are these required??
COPY README.md .
COPY CHANGES.txt .

# Install packages listed in requirements.txt
# Note we are not installing them in a virtualenv
# because:
#   A: It's complicated getting virtualenv to work inside Docker
#   B: Dependencies are already isolated via Docker, so there's no need for virtualenv
RUN pip install -r requirements.txt

# Install the test packages (specified in setup.py I think)
RUN pip install -e ".[testing]"

# Remove directory since we don't need the files anymore
# AND because we are going to mount the repository at temp dir since we don't actually need the files for anything else
RUN rm -r ${DIRECTORY}

# less is useful as a pager when debugging with pdb
# htop is useful
RUN apt update && apt install -y less htop

# Note the WORKDIR is still the same place that
# we will bind mount the repository from docker-compose
CMD ["pserve", "production.ini"]
