# Streak
An app to help you focus on your goals,
share your streaks with friends on your 
preferred platform. 


![Main Screen](docs/img/home.png)

![Login Screen](docs/img/login.png)

This project was developed as part of HackHub 2022.


## Setup 
Create a `.env` file. Copy the sample `.env.sample` as `.env`
and add the appropriate values there.

```bash
docker build . -t streak:latest
```



## Run 
```bash 
python -m streak
```
or
```bash
docker run -p 5000:5000 streak:latest
```



