#!/usr/bin/env bash

CORPUS_PATH=$1

print_raw_stats() {
    num_arts=$(find "$1" -type f | wc -l)
    printf "\nThe corpus has %s articles\\n" "$num_arts"
    printf "Source wise statistics:\\n"
    printf "+-----------------------------------------+\\n"
    printf "| %-15.15s | %-8s | %-8s |\\n" "source" "articles" "size"
    printf "+-----------------------------------------+\\n"
    for dir in "$1"/*; do
        name=$(basename "$dir")
        num_arts=$(find "$dir" -type f | wc -l)
        size=$(du "$dir" -h | cut -f1)
        printf "| %-15.15s | %-8d | %-8s |\\n" "$name" "$num_arts" "$size"
    done
    printf "+-----------------------------------------+\\n"
}

print_processed_stats() {
    lines=$(wc -l "$1" | cut -d' ' -f1 | numfmt --to=si)
    uniqlines=$(awk '!($0 in a) {a[$0];print}' "$1" | wc -l | cut -f1 | numfmt --to=si)
    tokens=$(tr ' ' '\n' < "$1" | wc -l | cut -f1 | numfmt --to=si)
    uniqtokens=$(tr ' ' '\n' < "$1" | awk '!($0 in a) {a[$0];print}' | wc -l | cut -f1 | numfmt --to=si)
    printf "Number of lines: %s\\n" "$lines"
    printf "Number of unique lines: %s\\n" "$uniqlines"
    printf "Number of tokens: %s\\n" "$tokens"
    printf "Number of unique tokens: %s\\n" "$uniqtokens"
}

if [ -d "$CORPUS_PATH" ]; then
    print_raw_stats "$CORPUS_PATH"
elif [ -f "$CORPUS_PATH" ]; then
    print_processed_stats "$CORPUS_PATH"
else
    echo "$CORPUS_PATH is not valid"
    exit 1
fi
