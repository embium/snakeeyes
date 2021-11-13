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

- https://github.com/kvesteri/wtforms-alchemy/issues/158
- https://github.com/hadolint/hadolint
- https://github.com/nickjj/docker-flask-example
- https://nickjanetakis.com/blog/docker-tip-89-lint-your-dockerfile-with-hadolint


-----------------------------------
Video Timestamps
-----------------------------------

0:34 -- Updating Postgres and Redis
3:00 -- Updating Python and Node
4:36 -- Updating all of our Python packages
11:13 -- Introducing Hadolint to lint our Dockerfile
12:20 -- Going back to committing our Python package updates
12:44 -- And we're back to Hadolint
16:03 -- Going over which front-end dependencies we'll be updating
19:25 -- Running Yarn outdated to figure out what we're updating
20:38 -- Updating Font Awesome and jQuery
21:24 -- When is the Flask course going to be re-written?
23:47 -- Do our tests still pass? Yep!
25:03 -- Does interacting with Stripe still work? Yes!
26:55 -- What will be in the next update?
