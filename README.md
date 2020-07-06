# PAPI
Process Wrapper API. The purpose of this API is to provide a generic submit/status REST/JWT interface, to submit slurm jobs on a remote machine.

The scheduling of slurm jobs is done via ssh. For this the API uses the paramiko python module.

A "job" is seperated into 4 different phases. In each Phase a command on a remote SSH machine is executed.

The command is expected to return an sbatch output with the slurm id of the job and the machine, running the job.

# Use Docker to run API
```
    docker build -t papi .
    docker -p 5000:5000 run papi

```

# Demo of the API with docker
This demo shows the basic functionality of the API without requiring actually
submitting real jobs on a SLURM cluster. The following steps will start the API
within a container, submit a demo job via the API, store job information within
the database and retrieve job status information from the API. The status
message for the finished job shows a successful job with results that can be
downloaded.

* Start the Docker container as mentioned above
* Use curl to submit a demo job:
```
$ curl --header "Content-Type: application/json" --request POST --data '{"seeding_date": "sub15days", "irrigation": "true", "nutrition_factor": "0.25", "phenology_factor": "1", "debug": "1"}' http://localhost:5000/submit/

{
  "message": 1, 
  "status": "created"
}


``` 
* Use curl to get the job status:
```
$ curl --header "Content-Type: application/json" --request GET http://localhost:5000/status/1

{
  "message": {
    "message": "{'message': ''}", 
    "result_path": "/dss/dssfs01/pn56go/pn56go-dss-0000/process/UC5/results/test", 
    "result_webdav": "http://lobcder.process-project.eu:32432/lrzcluster/results/test"
  }, 
  "status": "finished"
}


```

# Start API Webserver
```
python main.py

```
# Deploy to production
To deploy the API to production, use the WSGI-files for apache2 or nginx and configure the
appropriate paths within:
```
activate_this = '<PATH-TO-PYTHON-ENV>/bin/activate_this.py'
sys.path.append('<PATH-TO-SRC-DIR>')

```


# Possible Request Methods
```
http://localhost:5000/submit/<id>
http://localhost:5000/status/<id>
```

# Test the API
```
python test.py --id <id> --method [submit|status] [--payload <json>]
```

# API Configration

Implemented in config.py

```
config['DEBUG'] = True  			#API Debug Flag
config['PORT'] = '5000' 			#API HTTP Port
config['SSH_HOSTNAME'] = 'localhost' 		#SSH Hostname
config['SSH_USERNAME'] = 'user' 		#SSH Username
config['SSH_PASSWORD'] = 'pass' 		#SSH Password
config['STATUS_COMMAND'] = "echo" 		#SSH CMD executed on Status request
config['SUBMIT_COMMAND'] = "echo" 		#SSH CMD executed on submit request
config['SUBMIT_FIELDS_REQUIRED'] = ['test'] 	#Mandatory Payload fields for submit requests
```

# Use API for different Use Cases / Applications
This API is written for UC5 of PROCESS. It is however easily adoptable for
different use cases, that need a proxy API as an intermediary between job
submission systems.

To adapt this API for different scenarios, first configure the API in
`config.py`. Second, review the application logic of submission phases within
`papi/handler/submit.py` and `papi/handler/status.py`. Finally configure
`cluster/wrapper.sh` for the actual job submission on the cluster and copy it to
a login-node on your cluster. 
