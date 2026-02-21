set -B                  # enable brace expansion
for i in {1..1450}; do
    curl https://www.pqdi.cc/static/icons/$i.gif -o $i.gif
done

