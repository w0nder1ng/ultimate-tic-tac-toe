#!/bin/bash

# create env file with SECRET as random bytes
echo "SECRET_KEY=$(openssl rand -hex 16)" > .env
