# COMP41720 Group Project - Video Streaming Service

A distributed and scalable video streaming service. Users can create accounts, upload videos, and stream videos with a desired quality as well as automatically generated subtitles.

## Members and Responsibilities

* Ryan Jeffares 23201777 - Audio, Streaming
* Yash Singh Pathania 24204265 - MongoDB, Postgres, K8s
* Euan Leith 24108821 - User accounts, Redis
* Nishal Koshy Philip 24241487 - Video Uploading and Processing
* Sinem Taşkın 24283182 - Broker and Client

## Running

Install Docker, Kubernetes and Minikube.

```bash
$ minikube start
$ sudo chmod +x apply_all_k8s.sh
$ ./apply_all_k8s.sh
```

To expose the load balancing services locally:

```bash
$ sudo minikube tunnel
```

Keep this terminal window open.

To check the status of the services:

```bash
$ minikube dashboard
```
