from nicegui import ui, app, native
from app.startup import startup

app.on_startup(startup)

ui.run(title="ANCHOR",
       port=native.find_open_port(),
       favicon='⚓',
       native=True,
       #css='body {background-color: #111927; background-image: radial-gradient(at 47% 33%, hsl(162.00, 77%, 40%) 0, transparent 59%), radial-gradient(at 82% 65%, hsl(218.00, 39%, 11%) 0, transparent 55%);',
       #reload=False
       )
