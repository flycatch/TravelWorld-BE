
<h1 align="center"> ComBus </h1> <br>
<p align="center">
  <a href="https://gitpoint.co/">
    <img alt="Logo" title="Logo of the project" src="https://combus.flycatchtech.in/assets/combus.svg" width="450">
  </a>
</p>

<p align="center">
Embark on a Journey of Convenience with Combus – Your Modern Solution for Effortless Bus Ticket Bookings. Experience Connectivity, Ease, and Innovation in Travel. 
</p>


## Table of Contents

- [Introduction](#introduction)
- [Requirements](#requirements)
- [Steps to run the project](#steps-to-run-the-project)
- [Deployment](#deployment)


# Introduction
ComBus is an online ticketing platform, Combus caters to the diverse needs of travelers, providing a user-friendly interface for the hassle-free booking of bus tickets. Whether you're planning a quick city getaway or a long-distance journey, Combus offers a comprehensive selection of routes, ensuring connectivity and convenience.
This platform is a Proof of Concept (POC) project, designed to showcase the potential of modern technology in simplifying and enhancing the process of reserving bus seats.

## Requirements

 - Python version `3.10.12`
 - Django version `4.3.1`


# Steps to run the project

## Install packages

````bash
    pip install -r .requirements.txt
````

## prepare and runserver
```bash
    ./manage.py migrate
    ./manage.py runserver
```

## create superuser
```bash
    ./manage.py createsuperuser
```


# Deployment


#### For DEV Environment

```
    git pull origin dev
```

#### For Production Environment

```
    git pull origin dev
```

### Application Run
```
    docker compose up --build -d
```

### Application Down
```
    docker compose down
```

### Remove Static
```
    docker compose down
    docker volume rm combus_static_volume
```

### Load Static
```
    docker compose -f docker-compose.yml exec web python manage.py collectstatic
```

### Apply Migrations
```
    docker compose -f docker-compose.yml exec web python manage.py migrate
```

### Enter Shell
```
    docker compose -f docker-compose.yml exec web python manage.py shell
```