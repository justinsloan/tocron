import subprocess
from nicegui import ui
from pathlib import Path

from app.class_PingCard import *
from app.class_ProjectTree import *


def startup():
    dark_mode = ui.dark_mode(True)

    # Header Row
    with ui.header().classes(replace='row items-center pl-5 pr-5 dark:bg-gray-900') as header:
        # Menu
        with ui.button(icon='menu').classes('m-1'):
            with ui.menu() as menu:
                ui.menu_item('Ping Card', lambda: add_ping_card(container=main_body))
                ui.menu_item('Open Project...', lambda: ui.notify('Selected item 2'))
                ui.separator()
                ui.menu_item('Keep Menu Open After Click', lambda: ui.notify('Keep Menu Open'), auto_close=False)
                ui.separator()
                ui.menu_item('Quit', lambda: shutdown())
        ui.button(icon='add', on_click=lambda: add_ping_card(container=main_body)).classes('m-1')

        # Right
        ui.space()
        project_name = ui.label('Amity').classes('text-2xl')
        ui.space()
        ui.switch().bind_value(dark_mode)#.on_value_change(lambda: switch_dark_mode)

    # Project Tree
    #with ui.left_drawer() as left_drawer:
    #    project = ProjectTree(project_path='~/Downloads/merefaith-jekyll/')

    # Footer
    with ui.footer(value=False) as footer:
        with ui.row():
            with ui.expansion('Contact Support', icon='help').classes('w-full'):
                ui.label('inside the expansion')
                
            with ui.expansion('Logs', icon='file').classes('w-full'):
                log = ui.log().classes('w-full h-20')
                log.push('Started...')

    with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20):
        ui.button(on_click=footer.toggle, icon='contact_support').props('fab')

    # Main Body: All card classes should be contained in main_body
    main_body = ui.element('div').classes('flex size-full gap-1')
    add_ping_card(container=main_body, target='10.20.30.5')
        
def shutdown():
    # need a graceful shutdown
    exit()

# can we use one handler to add all card types?
# this way we only need one function instead of a func per type.
# DNS (lookup, MX, TXT, etc.), cURL, Python, SH cards
def add_ping_card(container: ui.element, target=''):
    if not target:
        target = 'None'
    PingCard(target=target, container=container)
    container.update()
