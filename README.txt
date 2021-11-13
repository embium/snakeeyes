-----------------------------------
Getting everything up and running
-----------------------------------

1. Copy .env.example to .env

2. Add your email and Stripe credentials to your .env file.
  (use your instance/settings.py file from section 20's code as a reference)

3. Open a terminal configured to run Docker and then run:

docker-compose down -v
docker-compose build --no-cache
docker-compose up
./run flask db reset --with-testdb
./run flask add all
./run flake8
./run pytest


-----------------------------------
Troubleshooting
-----------------------------------

Q: You get a permission error when upping the project

A: Some unzipping tools remove executable file permission bits from files, so you
might need to run the command below to update a few shell script permissions:

chmod +x run bin/*

You'll want to run that if you get an error when upping everything that's
related to permissions or you notice those files are not executable. This will
depend on your terminal but usually executable files will be green in color.


-----------------------------------
Reference Links
-----------------------------------



-----------------------------------
Video Timestamps
-----------------------------------
