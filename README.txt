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

Copied from cgi-bin/container.py:

# This script takes POST data

# POST variables expected:

# cwidth    - Container width
# cdepth    - Container depth
# cheight   - Container height

# name[]    - Array of package identifiers
# length[]  = Array of package depths
# width[]   = Array of package widths
# height[]  - Array of package heights
# qty[]     - Array of how many individual packages this entry represents

# ***** WARNING ABOUT FLAGS *****
# Flags are usually handled by checkboxes. However, POST data only sends the checkboxes that have been checked,
# with no indication which row it belongs to. Therefore, every checkbox should be overwritten to send a value
# of either 'checked' or 'unchecked'

# top[]     = Array of flags for whether this package may have others below it
# bottom[]  - Array of flags for whether this package may have others below it
# rotation[]- Array of flags for whether this package may be rotated in space or not    
