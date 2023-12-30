#!/bin/bash

# Check if arguments are provided
if [ -z "$1" ] || [ -z "$2" ]
then
    echo "Not all arguments supplied. Please provide a path, input file, and output file."
    exit 1
fi

# Replace the string in the file
sed "s|/path/to|$1|g" $2 