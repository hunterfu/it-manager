while read line
do
   code=`echo "$line" |cut -f 1`
   #echo "code = $code"
   name=`echo "$line" |cut -f 2` 
   #echo "name = $name"
   #echo 
   echo "code = $code name=$name"
   ../update_stock_data.py -s "$code" -t "$name"
   #exit 0
done < $1
