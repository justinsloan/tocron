import re
import asyncio
import subprocess
import dns.resolver
from nicegui import ui
from app.helper_functions import *
from app.class_Registry import *


#--------------------------------------------------------------------
# Write about the attrs here
# self.title            STR
# self.target           STR
# self.interval         INT
# self.timer.active     BOOL
#--------------------------------------------------------------------


class PingCard(metaclass=Registry):
    def __init__(self, title: str, target: str, container: ui.element, interval=60, start_active=True):
        # instantiate variables
        self.container = container
        self.interval = interval
        self.ping_history = []
        self.target = ''
        self.result = ''
        self.active = ''
        self.in_trash = 'false' # <-- str, not bool

        # styles
        self._glass = 'backdrop-filter: blur(12px) saturate(165%); -webkit-backdrop-filter: blur(12px) saturate(165%); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.125);'
        _card_classes = 'm-3 p-0'

        # creates timer and performs initial ping
        self.timer = ui.timer(interval=self.interval, callback=lambda: asyncio.create_task(self.ping()))
        if not start_active:
            self.timer.active = False

        with self.container:
            self.card = ui.card().classes('m-2 w-full sm:max-w-56 break-inside-avoid').style(self._glass)
            with self.card:
                self.title = ui.label(title).classes('m-2 ml-3 text-xl font-bold')
                self.front = ui.card_section().classes(_card_classes)
                with self.front:
                    self.card_front(target)

                self.back = ui.card_section().classes(_card_classes)
                self.back.set_visibility(False)
                with self.back:
                    self.card_back()

    def card_front(self, target: str):
        _button_props = 'flat no-shadow'
        _button_classes = 'text-xs text-white p-1'

        self.target = ui.label(target)
        self.result = ui.label('0 ms')

        with ui.element('div') as self.chart_div, ui.card():
            self.chart_div.set_visibility(False)
            self.chart_div.classes('mx-auto justify-center rounded-lg').style(self._glass)
            self.ping_chart = ui.echart({
                'xAxis': {'type': 'category', 'show': False},
                'yAxis': {'type': 'value', 'name': 'Response Time (ms)'},
                'grid': {'show': False},
                'series': [{'type': 'line', 'data': self.ping_history}],
            }, theme={'color': ['#b687ac', '#28738a', '#a78f8f'],
                      'backgroundColor': '#1d1d1d',
            }, on_point_click=ui.notify,
            ).on('click', lambda: self.ping_chart.update())

        with ui.row().classes('mt-1 p-0 w-full'): #.style(self._glass):
            ui.button(icon='network_ping', on_click=lambda: asyncio.create_task(self.ping())).props(_button_props).classes(
                _button_classes)
            ui.button(icon='bar_chart', on_click=self.show_chart).props(_button_props).classes(_button_classes)
            ui.button(icon='fingerprint', on_click=self.fingerprint).props(_button_props).classes(_button_classes)
            ui.space()
            ui.button(icon='settings_applications', on_click=self.flip_card).props(_button_props).classes(_button_classes)

    def card_back(self):
        with ui.input('Title') as self.title_input:
            self.title_input.set_value(self.title.text)

        with ui.input('Target') as self.target_input:
            self.target_input.set_value(self.target.text)
            self.target_input.on('update:model-value', lambda e: asyncio.create_task(self.ping(self.target_input.value)))
            with self.target_input.add_slot('append'):
                self.target_status_icon = ui.icon('network_ping') \
                                          .on('click', lambda e: asyncio.create_task(self.ping(self.target_input.value))).classes('cursor-pointer')

        ui.switch('Monitor').props('color=grey').bind_value_to(self.timer, 'active').set_value(True)

        with ui.expansion('More Options').classes('mb-2').style(self._glass):
            title_checkbox = ui.checkbox('Show card title').classes('pr-2').style(self._glass)
            title_checkbox.set_value(True)
            self.title.bind_visibility_from(title_checkbox, 'value')
            ui.label('Danger Zone').classes('text-xs text-red')
            ui.button(icon='delete', on_click=self.trash).props('flat ').classes('text-xs text-red bg-red-100').style(self._glass)

        ui.button(icon='save', on_click=self.save_settings).props('flat no-shadow').classes('text-xs').style(self._glass)

    def flip_card(self):
        if self.front.visible:
            # flip to back
            self.front.set_visibility(False)
            self.back.set_visibility(True)
            self.set_background('bg-black/30')
        else:
            # flip to front
            self.front.set_visibility(True)
            self.back.set_visibility(False)

    def show_chart(self):
        if self.chart_div.visible:
            # hide the chart
            self.chart_div.set_visibility(False)
        else:
            # show the chart
            self.ping_chart.update()
            self.chart_div.set_visibility(True)

    def save_settings(self):
            self.flip_card()
            self.title.set_text(self.title_input.value)
            self.set_target(self.target_input.value)

    def set_target(self, new_target: str) -> None:
        """Changes the ping target."""
        self.target.set_text(new_target)
        asyncio.create_task(self.ping())

    def set_background(self, classes: str):
        if not self.timer.active:
            self.card.classes(replace='')
        else:
            self.card.classes(replace=classes)

    def fingerprint(self):
        # this should be an async process in helper_functions
        registrar, expiration = check_registrar(self.target.text)
        query = dns.resolver.resolve(self.target.text)

        with ui.dialog() as dialog, ui.card().classes('p-3').style(self._glass):
            with ui.row().classes('items-center p-0 m-0').style(self._glass):
                ui.icon('fingerprint').classes('m-0 pb-2 pl-2 pt-2 text-3xl')
                ui.label(self.target.text).classes('m-0 pr-2 text-xl')

            with ui.row().classes('pl-1'):
                ui.label('Registrar: ' + registrar)
                ui.label('Expiration: ' + expiration)
                for ip in query:
                    ip_addr = ip.to_text()
                    country = get_country_from_ip(ip_addr)
                    if country:
                        ui.label('IP: ' + ip_addr + f' [{country}]')
                    else:
                        ui.label('IP: ' + ip_addr)

            ui.button('Close', on_click=dialog.close).style(self._glass)
        dialog.open()

    def trash(self):
        self.timer.cancel()
        self.in_trash = 'true' # <-- str, not bool
        self.card.delete()

    def _get_properties(self):
        values = dict(type = 'ping',
                      active = self.timer.active,
                      title = self.title.text,
                      target = self.target.text,
                      trash = self.in_trash)
        return values

    async def sh_ping(self, target: str = '') -> subprocess.CompletedProcess:
        """
        Execute ping without blocking the event loop.
        """
        # Run the command in a thread‑pool executor so the loop stays free.
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None,
            lambda: subprocess.run(['ping', '-c', '1', f'{target}'], capture_output=True, text=True)
        )

    async def ping(self, target=''):
        if not self.timer.active: return # do nothing when switched off

        if not target:
            target = self.target.text

        try:
            response = await asyncio.wait_for(self.sh_ping(target), timeout=5)
        except asyncio.TimeoutError:
            self.result.set_text('Ping timed out.')
            self.set_background('bg-yellow-300/20')
            self.target_status_icon.classes(replace='text-yellow')
            return

        match = re.search(r'(\d+)(?: packets)? received', response.stdout)

        if not match:
            self.result.set_text(response.stderr)
            self.set_background('bg-red-500/20')
            self.target_status_icon.classes(replace='text-red')
        else:
            if not int(match.group(1)) > 0:
                self.result.set_text('Red: Ping Failed')
                self.set_background('bg-red-500/20')
                self.target_status_icon.classes(replace='text-red')
            else:
                line = response.stdout.splitlines()[-1]              # example: round-trip min/avg/max/stddev = 45/60/67/0.000 ms
                numerical_part = line.split('=')[1].strip()          # split on '=' to get just '45/60/67/0.000 ms'
                parts = numerical_part.replace(' ms', '').split('/') # split on '/' to get a list of [45, 60, 67, 0]

                if parts:
                    min_val = parts[0]
                    avg_val = parts[1]
                    max_val = parts[2]
                    #mdev_val = match.group(4)

                    speed = {
                        'min': min_val,
                        'avg': avg_val,
                        'max': max_val
                        #'mdev': mdev_val
                    }

                    self.result.set_text(str(speed['avg']) + ' ms')
                    self.set_background('bg-green-500/20')
                    self.target_status_icon.classes(replace='text-green')
                    self.ping_history.append(avg_val)
                    if self.chart_div.visible:
                        self.ping_chart.update()
                else:
                    self.result.set_text('Red: String parse error')
                    self.target_status_icon.classes(replace='text-yellow')