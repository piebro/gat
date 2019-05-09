pathToFile=$1
path=${pathToFile%/*}
filename=$(basename $pathToFile)
filenameWithoutExt=${filename%.*}

cat $1 | \
python center-rescale-svg.py -l | \
python unify-line-width.py -l | \
python add-text.py "piebro.de?s=$filenameWithoutExt" -l | \
python add-background.py -l \
-o "$path/plotready-$filename"