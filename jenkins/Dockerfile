FROM jenkins/jenkins:lts-jdk21

USER root

# CLI de Docker + plugin de compose, copiados desde la imagen oficial docker:cli.
# Jenkins usará el daemon del host a través de /var/run/docker.sock.
COPY --from=docker:cli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=docker:cli /usr/local/libexec/docker/cli-plugins/docker-compose /usr/local/libexec/docker/cli-plugins/docker-compose

# Evita el error "detected dubious ownership" con carpetas montadas
RUN git config --system --add safe.directory '*'

USER jenkins

# Plugins declarados como código (ver plugins.txt)
COPY --chown=jenkins:jenkins plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt

# Jenkins Configuration as Code (JCasC): sin asistente de instalación
ENV JAVA_OPTS="-Djenkins.install.runSetupWizard=false"
ENV CASC_JENKINS_CONFIG=/casc/jenkins.yaml
COPY --chown=jenkins:jenkins jenkins.yaml /casc/jenkins.yaml