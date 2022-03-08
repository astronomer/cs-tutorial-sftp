FROM quay.io/astronomer/ap-airflow:2.2.4-2-onbuild

# Need the openssh-client to add the fingerprint
USER root
RUN apt-get update && apt-get install -y \
    openssh-client \
    && rm -rf /var/lib/apt/lists/*
USER astro

# Create test file that will get uploaded via sftpoperator
RUN mkdir -p /tmp/single-file
RUN echo "Hello World!" > /tmp/single-file/test-file.txt
RUN mkdir /home/astro/.ssh

#RUN ssh-keyscan -H <YOUR-HOST> > /home/astro/.ssh/known_hosts #added this as a bashoperator but it adds the fingerprint necessary to run sftp components
