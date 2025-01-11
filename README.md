# Sync Outlook ICS to google agenda

## Why ?

Because I needed it.

## Install

- Get python 3.12 on your system
- Install uv: https://docs.astral.sh/uv/getting-started/installation/
- Install marimo: `pip install marimo`
- Get a `Credentials.json` for google: https://developers.google.com/calendar/api/quickstart/python

## Running

### As a notebook

Recommanded for the first run. This way you can see the cells and have a feel of what's happening
```bash
$ marimo edit --sandbox google-notebook.py -- -ics URL_OF_ICS -google GOOGLE_CAL_URL
```

### As a script

Once everything is running smoothly you can simply run the notebook as a script.

```bash
$ uv run google-notebook.py -- -ics $URL_OF_ICS -google $GOOGLE_CAL_URL
```

## Technical decision

### Marimo

I just heard about it when developping the script, so I decided to give it a try. The handling of variables
on reactive cells (i.e. variable can be declared in only one place) is a bit annoying. But the counterpart
(run as a script) is pretty nice.
