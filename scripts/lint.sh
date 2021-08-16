#!/bin/bash

find -name "*.py" | xargs black --check
