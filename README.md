# ultimate-tic-tac-toe
A server to host ultimate tic-tac-toe tournaments

## Running the server

First, generate a secret using `init.sh`:
```bash
./init.sh
```

### Docker

In the root of the repository, run:
```bash
docker compose up
```

To run the server in development mode, run:
```bash
ENV=dev docker compose up
```

By default, Flask's auto-reloading feature is turned on.

### Native

First, load the secret key:
```bash
source .env
```

Then, install the necessary python libraries (I recommend a venv):
```bash
python3 -m venv ./venv
source venv/bin/activate
pip install -r server/requirements.txt
```

Install mongodb (see [here](https://www.mongodb.com/docs/manual/installation/))

Start a mongod instance:

For Mac: 
```bash
brew services start mongodb-community@7.0
```

For Linux:
```bash
mongod
```

Start the app:
```bash
cd server && flask --app app.py --debug run
```
