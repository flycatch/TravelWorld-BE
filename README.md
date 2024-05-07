
<h1 align="center"> Explore World </h1> <br>
<p align="center">
  <!-- <a href="https://gitpoint.co/">
    <img alt="Logo" title="Logo of the project" src="https://combus.flycatchtech.in/assets/combus.svg" width="450">
  </a> -->
</p>

<p align="center">
Embark on a Journey of Convenience with Explore World – Your Modern Solution for Effortless Tour Package Bookings.
</p>


## Table of Contents

- [Introduction](#introduction)
- [Requirements](#requirements)
- [Steps to run the project](#steps-to-run-the-project)
- [Deployment](#deployment)


# Introduction
Explore World Travel and Tourism Booking Website aims to revolutionise the way travel and tourism services are offered and experienced.The project encompasses the development of a robust and user-friendly online platform that caters to the diverse needs of Super Admins, Agents, and End Users in the travel and tourism industry.

## Requirements

 - Python version `3.10.12`
 - Django version `5.0.1`


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
    docker volume rm explore_static_volume
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