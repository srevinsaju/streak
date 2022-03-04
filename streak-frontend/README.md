# Streak Web UI

```bash
yarn install
yarn run build:dev # to convert *.ts to *.js

# pull in the required css
mkdir -p dist/
ln -sr $(realpath static/css) dist/.

# run a basic python server at localhost:8000
yarn run serve:dev # to start the server
```

