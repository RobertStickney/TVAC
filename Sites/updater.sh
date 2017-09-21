while inotifywait -r -e modify,create,delete /home/david/Desktop/tvac/TVAC/Sites; do
    rsync -avz /home/david/Desktop/tvac/TVAC/Sites/* root@192.168.99.1:~/davidTesting/
done