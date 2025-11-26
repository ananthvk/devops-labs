```
docker run -d \
  --user root \
  -p 8080:8080 -p 50000:50000 \
  --name jenkins \
  -v ./jenkins_home:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /usr/bin/docker:/usr/bin/docker \
  -v /home/shank/code/bmsce/devops/6-grafana-realtime-monitoring/delivery_monitoring:/files \
  jenkins/jenkins:lts
```