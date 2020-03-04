from random import randint, choice

f = open('demo.html','w')
f.write('<html><body><form action="/cgi-bin/container.py" method="POST">\n')
f.write('<input type="text" name="cwidth" value="50">\n')
f.write('<input type="text" name="cdepth" value="100">\n')
f.write('<input type="text" name="cheight" value="50"><br/>\n\n')
f.write('<input type="text" name="palette_load" value="checked"><br/>\n\n')
f.write('<input type="text" name="pwidth" value="50"><br/>\n\n')
f.write('<input type="text" name="pdepth" value="50"><br/>\n\n')
f.write('<input type="text" name="pheight" value="5"><br/>\n\n')

checked = ['unchecked','checked']

for i in range(randint(20,100)):
    f.write('<input type="text" name="name[]" value="cargo%d">\n' % i)
    f.write('<input type="text" name="length[]" value="%d">\n' % randint(5,50))
    f.write('<input type="text" name="width[]" value="%d">\n' % randint(5,50))
    f.write('<input type="text" name="height[]" value="%d">\n' % randint(5,50))
    f.write('<input type="text" name="qty[]" value="%d">\n' % randint(1,20))
    f.write('<input type="text" name="weight[]" value="%d">\n' % randint(30,500))
    f.write('<input type="text" name="rotation[]" value="%s">\n' % choice(checked))
    f.write('<input type="text" name="top[]" value="%s">\n' % choice(checked))
    f.write('<input type="text" name="bottom[]" value="%s">\n' % choice(checked))
    f.write('<input type="text" name="rotation_standard[]" value="%s">\n' % choice(checked))
    f.write('<input type="text" name="rotation_side[]" value="%s">\n' % choice(checked))
    f.write('<input type="text" name="rotation_up[]" value="%s">\n' % choice(checked))
    f.write('<br/>\n')

f.write('<input type="submit">\n</form></body></html>\n')
f.close()    