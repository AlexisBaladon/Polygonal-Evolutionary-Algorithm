#!/bin/bash
gunicorn -c gunicorn_config.py app:app