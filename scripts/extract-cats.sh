
SOURCE_PATH=$1
SOURCE_NAME=$(basename "$SOURCE_PATH")


touch tmp1
rm tmp1
touch tmp1

for file in "$SOURCE_PATH"/*
do
    ag "$SOURCE_NAME" "$file" | ag -o -m 1 "(?<=/)[^/.]+(?=/)" 2> /dev/null >> tmp1;
done

sort tmp1 | uniq -c | tee cats
rm tmp1
