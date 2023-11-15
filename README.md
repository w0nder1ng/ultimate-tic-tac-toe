# ultimate-tic-tac-toe
A server to host ultimate tic-tac-toe tournaments

## Running the server

First, initialize all submodules:
```bash
git submodule update --init --recursive
```

Next, generate a secret using `init.sh`:
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
