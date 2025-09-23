import logging
import subprocess
from nicegui import ui
from pathlib import Path

#from app.helper_functions import *
from app.local_dataclasses import *
from app.class_Registry import *
from app.class_PingCard import *

# DNS (lookup, MX, TXT, etc.), cURL, Python, SH cards

def startup():
    dark_mode = ui.dark_mode(True)

    _glass = 'backdrop-filter: blur(12px) saturate(148%); -webkit-backdrop-filter: blur(12px) saturate(148%); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.125);'

    # ------------------------------------------------------------
    # Header Row
    # ------------------------------------------------------------
    with ui.header().classes(replace='row items-center m-2 pl-5 pr-5 dark:bg-gray-900').style(_glass) as header:
        # Menu
        with ui.button(icon='menu').classes('mr-1 bg-transparent').style(_glass):
            with ui.menu() as menu:
                #@@ ui.menu_item('Ping Card', lambda: add_active_node(container=main_body))
                ui.menu_item('Ping Card', lambda: add_ping_card(main_container=main_body, drawer_container=left_drawer))
                ui.menu_item('Do Something...', lambda: ui.notify('Selected item 2'))
                ui.separator()
                ui.menu_item('Show Nodes List', lambda: left_drawer.set_value(True))
                ui.menu_item('Show Pending Tasks', lambda: right_drawer.set_value(True))
                ui.separator()
                ui.menu_item('Save Config', lambda: save_config())
                #ui.menu_item('Keep Menu Open After Click', lambda: ui.notify('Keep Menu Open'), auto_close=False)
                ui.separator()
                with ui.row().classes('m-0 p-0 justify-center items-center'):
                    ui.icon('contact_support').classes('m-0 p-0 text-2xl')
                    ui.menu_item('Support', lambda: footer.toggle)
                ui.menu_item('Quit', lambda: shutdown())
        #@@ ui.button(icon='add', on_click=lambda: add_active_node(container=main_body)).classes('bg-transparent').style(_glass)
        ui.button(icon='add',
                  on_click=lambda: add_ping_card(main_container=main_body, drawer_container=left_drawer)) \
                  .classes('bg-transparent').style(_glass)

        # Center-ish
        ui.space()
        ui.label('⚓ ANCHOR').classes('p-1 pl-2 pr-2 m-1 text-xl font-mono') \
                            .tooltip('Administrative Network Command Hub for Operations & Response')

        # Right
        ui.space()
        ui.switch().bind_value(dark_mode).props('color=grey')

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
    # Left Drawer:
    # ------------------------------------------------------------
    left_drawer = ui.left_drawer().classes('ml-2 mt-4 bg-gray-900/60') \
                         .style(_glass) \
                         .props('flat no-shadow bg-green')
    with left_drawer:
        # Header
        with ui.row().classes('items-center'):
            ui.button(icon='keyboard_arrow_left', on_click=lambda: left_drawer.set_value(False)).tooltip('Close drawer').props('flat no-shadow')
            ui.label('Nodes List')
        #inactive_nodes = ui.element('div').classes('flex size-full gap-1.5')

    # ------------------------------------------------------------
    # Right Drawer:
    # ------------------------------------------------------------
    with ui.right_drawer().classes('mr-2 mt-4 bg-gray-900/60').style(_glass) as right_drawer:
        # Header
        with ui.row().classes('items-center justify-items-end'):
            ui.label('Pending Tasks')
            ui.button(icon='keyboard_arrow_right', on_click=lambda: right_drawer.set_value(False)).tooltip('Close drawer').props('flat no-shadow')
    right_drawer.set_value(False)

    # ------------------------------------------------------------
    # Main Body: All card classes should be contained in main_body
    # ------------------------------------------------------------
    main_body = ui.element('div').classes('flex size-full gap-1.5')

    try:
        raw_data = load_data("nodes.json")
        loaded_nodes: List[Node] = [Node.from_dict(d) for d in raw_data]

    #     for node in loaded_nodes:
    #         if node.active == True:
    #             add_active_node(title=node.title,
    #                             target=node.target,
    #                             container=main_body)
    #         else:
    #             add_inactive_node(title=node.title,
    #                               target=node.target,
    #                               container=left_drawer)
    # except:
    #     add_active_node(target='localhost', container=main_body)

        for node in loaded_nodes:
            add_ping_card(main_container=main_body,
                          drawer_container=left_drawer,
                          title=node.title,
                          target=node.target,
                          start_active=node.active)

    except Exception as e:
        print(f"Error loading nodes: {e}")
        add_ping_card(main_container=main_body, drawer_container=left_drawer, target='localhost')


    left_drawer.update()

def add_ping_card(main_container: ui.element, drawer_container: ui.element, title: str = '', target: str = '', start_active: bool = True):
    if not target:
        target = 'localhost'
        title  = 'localhost'
    PingCard(title=title,
             target=target,
             interval=60,
             main_container=main_container,
             drawer_container=drawer_container,
             start_active=start_active)

def save_config():
    save_data("nodes.json", Registry._instances)
    ui.notify('Saved ' + str(len(Registry._instances)) + ' instances.')

def shutdown():
    # need a graceful shutdown
    save_config()
    exit()