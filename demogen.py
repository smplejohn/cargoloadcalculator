from random import randint, choice

f = open('demo.html','w')
f.write('<html><body><form action="/cgi-bin/container.py" method="POST">')

#length[] width[] height[] qty[] weight[] rotation[] top[] bottom[]

checked = ['unchecked','checked']

for i in range(randint(20,100)):
    f.write('<input type="text" name="name[]" value="cargo%d">' % i)
    f.write('<input type="text" name="length[]" value="%d">' % randint(5,50))
    f.write('<input type="text" name="width[]" value="%d">' % randint(5,50))
    f.write('<input type="text" name="height[]" value="%d">' % randint(5,50))
    f.write('<input type="text" name="qty[]" value="%d">' % randint(1,20))
    f.write('<input type="text" name="weight[]" value="%d">' % randint(30,500))
    f.write('<input type="text" name="rotation[]" value="%s">' % choice(checked))
    f.write('<input type="text" name="top[]" value="%s">' % choice(checked))
    f.write('<input type="text" name="bottom[]" value="%s">' % choice(checked))
    f.write('<br/>')

f.write('<input type="submit"></form></body></html>')
f.close()    