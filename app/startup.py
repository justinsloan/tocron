import logging
import subprocess
from nicegui import ui
from pathlib import Path

#from app.helper_functions import *
from app.local_dataclasses import *
from app.class_Registry import *
from app.class_PingCard import *


def startup():
    dark_mode = ui.dark_mode(True)

    # ------------------------------------------------------------
    # Header Row
    # ------------------------------------------------------------
    with ui.header().classes(replace='row items-center pl-5 pr-5 dark:bg-gray-900') as header:
        # Menu
        with ui.button(icon='menu').classes('m-1'):
            with ui.menu() as menu:
                ui.menu_item('Ping Card', lambda: add_ping_card(container=main_body))
                ui.menu_item('Open Project...', lambda: ui.notify('Selected item 2'))
                ui.separator()
                ui.menu_item('Save Config', lambda: save_config())
                #ui.menu_item('Keep Menu Open After Click', lambda: ui.notify('Keep Menu Open'), auto_close=False)
                ui.separator()
                ui.menu_item('Quit', lambda: shutdown())
        ui.button(icon='add', on_click=lambda: add_ping_card(container=main_body)).classes('m-1')

        # Right
        ui.space()
        project_name = ui.label('Anchor').classes('text-2xl')
        ui.space()
        ui.switch().bind_value(dark_mode)#.on_value_change(lambda: switch_dark_mode)

    # ------------------------------------------------------------
    # Footer
    # ------------------------------------------------------------
    with ui.footer(value=False) as footer:
        with ui.row():
            with ui.expansion('Contact Support', icon='help').classes('w-full'):
                ui.label('inside the expansion')
                
            with ui.expansion('Logs', icon='file').classes('w-full'):
                log = ui.log().classes('w-full h-20')
                log.push('Started...')

    # with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20):
    #     ui.button(on_click=footer.toggle, icon='contact_support').props('fab')

    # ------------------------------------------------------------
    # Main Body: All card classes should be contained in main_body
    # ------------------------------------------------------------
    main_body = ui.element('div').classes('flex size-full gap-1')

    try:
        raw_data = load_data("nodes.json")
        loaded_nodes: List[Node] = [Node.from_dict(d) for d in raw_data]

        for node in loaded_nodes:
            add_ping_card(title=node.title, target=node.target, container=main_body)
    except:
        add_ping_card(target='localhost', container=main_body)

# can we use one handler to add all card types?
# this way we only need one function instead of a func per type.
# DNS (lookup, MX, TXT, etc.), cURL, Python, SH cards
def add_ping_card(container: ui.element, title='', target=''):
    if not target:
        target = 'localhost'
        title  = 'localhost'
    PingCard(title=title, target=target, interval=60, container=container)
    container.update()

def save_config():
    save_data("nodes.json", Registry._instances)
    ui.notify('Saved ' + str(len(Registry._instances)) + ' instances.')

def shutdown():
    # need a graceful shutdown
    save_config()
    exit()