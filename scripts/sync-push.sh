#!/usr/bin/env bash

rsync -avu --exclude '.esphome' --exclude '.git' ./ home-nas:~/stacks/home-assistant/esphome/config/
