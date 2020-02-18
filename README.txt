README - Containers

Modules Used:
PyOpenGL    - For 3D rendering
Pillow      - For Image Processing

Files:
cgi-bin/container.py    - The actual CGI script. This goes in your cgi-bin folder
cgi-bin/freeglut.dll    - Needed for local testing on Windows installations
demogen.py              - Generates a random manifest form to demo.html, for testing

To Test With A Local Server:
python -m http.server --cgi --bind 127.0.0.1 8080