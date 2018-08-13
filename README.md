Server Set-up:

# Setting-up mongo: 
docker run --name mongoDB -d -p 27017:27017 --restart=always -v /db:/data/db mongo:2.6 --smallfiles

# Setting-up application:
Build:
docker build -t "rest-api" .

Start-up:
docker run -p 5002:5002 --restart=always --name restAPI -d rest-api