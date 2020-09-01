FROM node:10
 
COPY srv/ /srv/
WORKDIR /srv
 
RUN /usr/local/bin/npm install
 
CMD /usr/local/bin/node app.js
