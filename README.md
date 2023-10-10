# ultimate-tic-tac-toe
A server to host ultimate tic-tac-toe tournaments

## Running the server
First, either generate a secret or copy the sample one:
```bash
mv server/secret.fake server/secret
```

Then, install the necessary python libraries (I recommend a venv):
```bash
python3 -m venv ./venv
source venv/bin/activate
pip install flask pyjwt bcrypt pymongo
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

Eventually there will be a docker image but it isn't ready yet :((
