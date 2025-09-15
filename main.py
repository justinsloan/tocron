from nicegui import ui, app, native
from app.startup import startup

app.on_startup(startup)

ui.run(title="Amity",
       port=native.find_open_port(),
       favicon='🚀')#native=True#reload=False)
