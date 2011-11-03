unset http_proxy
unset FTP_PROXY
unset ftp_proxy
unset HTTP_PROXY 

IP=$(/sbin/ifconfig eth0 | grep "inet addr:" | awk '{ print $2 }' | cut -f2 -d":")

if [ $IP -eq "3.156.190.164" ]
then
 DJANGOWEB="http://3.156.190.164.nbcuni.ge.com/wikiexport/"
else
 DJANGOWEB="http://likewise.nbcuni.ge.com/wikiexport/"
fi

cd `pwd`"/elizabeth/blaster"
webdavcmd="tmp/cadaver.cmd"
urloutput="tmp/urloutput.txt"   # get the output from what we need to process.
curl -s $DJANGOWEB > $urloutput 
while read line
do
 wikipath=`echo $line | cut -d, -f1`
 wikifile=`echo $line | cut -d, -f2`
 url=`echo $line | cut -d, -f3`
 echo "Wikipath: " $wikipath

 curl -s $url > "tmp/$wikifile"    
 echo "open $wikipath" > $webdavcmd
 echo "put 'tmp/$wikifile'" >> $webdavcmd    
 echo Putting $url to $wikifile
 cadaver < $webdavcmd
 
done < $urloutput
