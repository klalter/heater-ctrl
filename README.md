# heater-ctrl
This code enables a local raspberry-pi to connect to a remote mongo-db. With that a rest-api can be set-up to control remotely the raspberry-pi.


Set-up the server: 

# Setting-up mongo: 
docker run -p 27017:27017 --restart=always -v db:/data/db mongo:3.2

# Setting-up application:
Build:
docker build -t "rest_api_srv" .

Start-up:
docker run -p 5002:5002 --restart=always rest-api
