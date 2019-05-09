#!/bin/sh

echo '$0 = ' $0 # the path to the current file
echo '$1 = ' $1 # inputname
echo '$2 = ' $2 # outputname
echo '$3 = ' $3 # fps 10 or 25
echo '$4 = ' $4 # rotchoice

{ # try
	mkdir -p $2/rgb

	if [ $4 = "n" ] || [ $4 = "N" ]
	then
	ffmpeg -i $1 -r $3 -vf scale=-1:320 $2/rgb/img%04d.png

	elif [ $4 = "y" ] || [ $4 = "Y" ]
	then
	ffmpeg -i $1 -r $3 -vf scale=320:-1,"transpose=1" $2/rgb/img%04d.png

	else
	    echo "Invalid choice. Choose y/n"
	    echo
	    exit 1
	fi
} || { # catch
	echo "Error. Processing failed."
}

#Counts the number of output files
imgnum=$(ls $2/rgb | wc -l)

echo "# colour images" > $2/rgb.txt
echo "#file: '$2'" >> $2/rgb.txt
echo "# timestamp filename" >> $2/rgb.txt

#Uses bc to calculate timestamp increment to 6 places
#No spaces around =
frameTime=$(bc <<< "scale=6; 1.0/$3")
timestamp=0.000000

for i in $(seq -f "%04g" $imgnum)
do
echo $timestamp rgb/img$i.png >> $2/rgb.txt
timestamp=$(bc <<< "scale=6; $timestamp+$frameTime")
done

echo
echo "Your files are ready, and have all been put in a single folder."
echo
