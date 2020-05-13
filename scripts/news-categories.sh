
corpus_path=$1
tmpfile=$(mktemp /tmp/webcrawl.XXXXXX)

fno=1
find "$corpus_path" -type f | while read fname
do
    echo -ne "Processing file $fno\r"
    grep "\"source\"" "$fname" | grep -Po "(?<=/)[a-z-]{0,20}(?=/)" >> "$tmpfile"
    fno=$((fno+1))
done

sort "$tmpfile" | uniq -c
rm "$tmpfile"
