while read line
do
   name=`echo $line |awk -F "," '{print $2}'` 
   code=`echo $line |awk -F "," '{print $1}'`
   code=`echo $code | sed  -r 's/^([a-zA-Z]+)([0-9]+)/\2.\1/'`
   code=`echo $code | tr [:lower:] [:upper:]`
   #echo -n $name
   #echo -e "\t$code"
   #echo 
   echo "code = $code name=$name"
   ../update_stock_data.py -s "$code" -t "$name" 
   #sleep 3
done < $1
