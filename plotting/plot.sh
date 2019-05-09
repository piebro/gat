tfile=$(mktemp /tmp/plotting.XXXXXXXXX)

python ./axidraw/axicli.py \
    --model 2 --preview --rendering 2 -o $tfile \
    $1

eog $tfile &

read -p "Do you wish to plot this graphic?" yn

if [ "$yn" != "y" ] && [ "$yn" != "Y" ]; then
    exit;
fi

python ./axidraw/axicli.py \
     --model 2 \
		 --speed_pendown 20 \
		 --speed_penup 60 \
		 --accel 20 \
		 --pen_pos_up 53 \
		 --pen_pos_down 30 \
    $1

python ./axidraw/axicli.py --mode align
