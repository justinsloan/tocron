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

    _glass = 'backdrop-filter: blur(12px) saturate(165%); -webkit-backdrop-filter: blur(12px) saturate(165%); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.125);'

    # ------------------------------------------------------------
    # Header Row
    # ------------------------------------------------------------
    with ui.header().classes(replace='row items-center pl-5 pr-5 dark:bg-gray-900') as header:
        # Menu
        with ui.button(icon='menu').classes('mr-1').style(_glass):
            with ui.menu() as menu:
                ui.menu_item('Ping Card', lambda: add_ping_card(container=main_body))
                ui.menu_item('Do Something...', lambda: ui.notify('Selected item 2'))
                ui.separator()
                ui.menu_item('Save Config', lambda: save_config())
                #ui.menu_item('Keep Menu Open After Click', lambda: ui.notify('Keep Menu Open'), auto_close=False)
                ui.separator()
                with ui.row().classes('m-0 p-0 justify-center items-center'):
                    ui.icon('contact_support').classes('m-0 p-0 text-2xl')
                    ui.menu_item('Support', lambda: footer.toggle)
                ui.menu_item('Quit', lambda: shutdown())
        ui.button(icon='add', on_click=lambda: add_ping_card(container=main_body)).style(_glass)

        # Right
        ui.space()
        ui.label('⚓ ANCHOR').classes('p-1 m-1 text-xl').style(_glass) \
                            .tooltip('Administrative Network Command Hub for Operations & Response')
        ui.space()
        ui.switch().bind_value(dark_mode)

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

    # ------------------------------------------------------------
    # Float Icon:
    # ------------------------------------------------------------
    # with ui.page_sticky(position='bottom-right', x_offset=20, y_offset=20):
    #     ui.button(on_click=footer.toggle, icon='contact_support').props('fab')

    # ------------------------------------------------------------
    # Main Body: All card classes should be contained in main_body
    # ------------------------------------------------------------
    main_body = ui.element('div').classes('flex size-full gap-1.5')

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