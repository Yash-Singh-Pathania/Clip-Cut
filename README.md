# COMP41720 Group Project - Video Streaming Service

A distributed and scalable video streaming service. Users can create accounts, upload videos, and stream videos with a desired quality as well as automatically generated subtitles.

## Members

* Ryan Jeffares 23201777
* Yash Singh Pathania 24204265
* Euan Leith 24108821
* Nishal Koshy Philip 24241487
* Sinem Taşkın 24283182

## Running

Install Docker, Kubernetes and Minikube.

MacOS/Linux:

```bash
$ sudo chmod +x run.sh
$ ./run.sh
```

Windows (Powershell with Administrator privileges):

```bash
$ ./run.ps1
```

Keep this terminal window open (it takes a long time to start!). On Mac/Linux, you will be prompted for your password to run the tunnel.

To check the status of the services:

```bash
$ minikube dashboard
```
