import re
import asyncio
import subprocess
import dns.resolver
from nicegui import ui
from app.helper_functions import check_registrar, get_country_from_ip, is_valid_hostname_or_ip
from app.class_Registry import Registry


#--------------------------------------------------------------------
# Write about the attrs here
# self.title            STR
# self.target           STR
# self.interval         INT
# self.timer.active     BOOL
#--------------------------------------------------------------------


class PingCard(metaclass=Registry):
    def __init__(self, title: str, target: str, main_container: ui.element, drawer_container: ui.element, interval=120,
                 start_active=True):
        # instantiate variables
        self.main_container = main_container
        self.drawer_container = drawer_container
        self.interval = interval
        self.ping_history = []
        self.target = ''
        self.result = ''
        self.active = ''
        self.in_trash = False

        # styles
        self._glass = 'backdrop-filter: blur(12px) saturate(165%); -webkit-backdrop-filter: blur(12px) saturate(165%); border-radius: 12px; border: 1px solid rgba(255, 255, 255, 0.125);'
        _card_classes = 'm-3 p-0'

        # creates timer and performs initial ping
        self.timer = ui.timer(interval=self.interval,
                              active=start_active,
                              callback=lambda: asyncio.create_task(self.ping()))

        container = self.main_container if start_active else self.drawer_container
        with container:
            self.card = ui.card().classes('w-full sm:max-w-56 break-inside-avoid').style(self._glass)
            with self.card:
                self.title = ui.label(title).classes('m-2 ml-3 text-xl font-bold')
                self.front = ui.card_section().classes(_card_classes)
                with self.front:
                    self.card_front(target)

                self.back = ui.card_section().classes(_card_classes)
                self.back.set_visibility(False)
                with self.back:
                    self.card_back()

                self.inactive = ui.card_section().classes(_card_classes)
                self.inactive.set_visibility(False)
                with self.inactive:
                    self.card_inactive()

        if not start_active:
            self._handle_activation_change()

    def card_front(self, target: str):
        _button_props = 'flat no-shadow'
        _button_classes = 'text-xs text-white p-1'

        self.target = ui.label(target)
        self.result = ui.label('0 ms')

        with ui.element('div') as self.chart_div:
            self.chart_div.set_visibility(False)
            self.chart_div.classes('w-full justify-center rounded-lg').style(self._glass)
            self.ping_chart = ui.echart({
                'xAxis': {'type': 'category', 'show': False},
                'yAxis': {'type': 'value', 'name': 'Time (ms)'},
                'grid': {'show': False, 'containLabel': True},
                'series': [{'type': 'line', 'data': self.ping_history}],
                'width': '85%',  # Added to make the chart fill the container width
                'height': '70%',  # Added to make the chart fill the container height
            }, theme={'color': ['#b687ac', '#28738a', '#a78f8f'],
                      'backgroundColor': '#1d1d1d',
                      }, on_point_click=ui.notify,
            ).classes('w-full flex').on('click', lambda: self.ping_chart.update())

        with ui.row().classes('mt-1 p-0 w-full'):
            ui.button(icon='network_ping', on_click=lambda: asyncio.create_task(self.ping())).props(_button_props).classes(
                _button_classes)
            ui.button(icon='bar_chart', on_click=self.show_chart).props(_button_props).classes(_button_classes)
            ui.button(icon='fingerprint', on_click=self.fingerprint).props(_button_props).classes(_button_classes)
            ui.space()
            ui.button(icon='flip', on_click=self.flip_card).props(_button_props).classes(_button_classes)

    def card_back(self):
        with ui.input('Title') as self.title_input:
            self.title_input.set_value(self.title.text)

        with ui.input('Target') as self.target_input:
            self.target_input.set_value(self.target.text)
            self.target_input.on('update:model-value', lambda e: asyncio.create_task(self.ping(self.target_input.value)))
            with self.target_input.add_slot('append'):
                self.target_status_icon = ui.icon('network_ping') \
                                          .on('click', lambda e: asyncio.create_task(self.ping(self.target_input.value))) \
                                          .classes('cursor-pointer')

        with ui.row().classes('items-center'):
            ui.switch('Monitor').on('change', self._handle_activation_change).props('color=green') \
                                .bind_value(self.timer, 'active').set_value(self.timer.active)
            ui.space()
            ui.icon('update').classes('m-o p-0 items-center text-2xl')
            ui.number(label='Seconds', value=self.timer.interval,
                      on_change=lambda e: setattr(self.timer, 'interval', int(e.value))) \
                      .classes(' m-0 p-0 w-12').props('borderless')

        # More Options
        with ui.expansion('More Options').classes('mb-2').style(self._glass):
            self.title_checkbox = ui.checkbox('Show title').classes('pr-2 w-full').style(self._glass)
            self.title_checkbox.set_value(True)
            self.title.bind_visibility_from(self.title_checkbox, 'value')
            ui.label('Danger Zone').classes('text-xs text-red')
            ui.button(icon='delete', on_click=self.trash).props('flat ').classes('text-xs text-red').style(self._glass)

        with ui.row():
            ui.space()
            ui.button(icon='done', on_click=self.save_settings).props('flat no-shadow').classes('p-1 pl-2 pr-2 text-xs text-white').style(self._glass)

    def card_inactive(self):
        with ui.row().classes('p-0 m-0 items-center w-full flex-nowrap'):
            self.inactive_title = ui.label(self.title.text).classes('text-sm font-bold')
            ui.space()
            ui.switch(on_change=self._handle_activation_change).bind_value(self.timer, 'active')

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
            self.inactive_title.set_text(self.title_input.value)
            self.set_target(self.target_input.value)

    def set_target(self, new_target: str) -> None:
        """Changes the ping target after validation."""
        if not is_valid_hostname_or_ip(new_target):
            ui.notify('Invalid target. Please enter a valid hostname or IP address.', color='warning')
            return
        self.target.set_text(new_target)
        asyncio.create_task(self.ping())

    def set_background(self, classes: str):
        if not self.timer.active:
            self.card.classes(replace='')
        else:
            self.card.classes(replace=classes)

    def fingerprint(self):
        # Validate target before performing external lookups
        target = self.target.text
        if not is_valid_hostname_or_ip(target):
            ui.notify('Invalid target for fingerprinting.', color='warning')
            return

        # WHOIS lookup (safe wrapper already handles exceptions)
        registrar, expiration = check_registrar(target)

        # DNS resolution with limited lifetime and exception handling
        ips = []
        try:
            answers = dns.resolver.resolve(target, lifetime=3)
            ips = [ip.to_text() for ip in answers]
        except Exception:
            ips = []

        with ui.dialog() as dialog, ui.card().classes('p-3').style(self._glass):
            with ui.row().classes('items-center p-0 m-0').style(self._glass):
                ui.icon('fingerprint').classes('m-0 pb-2 pl-2 pt-2 text-3xl')
                ui.label(target).classes('m-0 pr-2 text-xl')

            with ui.row().classes('pl-1'):
                ui.label('Registrar: ' + registrar)
                ui.label('Expiration: ' + expiration)
                for ip_addr in ips:
                    country = get_country_from_ip(ip_addr)
                    if country and country != 'Unknown':
                        ui.label('IP: ' + ip_addr + f' [{country}]')
                    else:
                        ui.label('IP: ' + ip_addr)

            ui.button('Close', on_click=dialog.close).style(self._glass)
        dialog.open()

    def trash(self):
        self.timer.cancel()
        self.in_trash = True # <-- Prevents class instance from being saved to disk
        self.card.delete()

    # def _apply_card_styling(self):
    #     """Applies classes and style to self.card based on active state and current background."""
    #     base_classes = 'w-full break-inside-avoid'
    #     active_width_class = 'sm:max-w-56'  # Specific to active state
    #
    #     current_card_style = ''
    #     current_card_classes = base_classes
    #
    #     if self.timer.active:
    #         # When active: apply max-w, _glass style, and current background
    #         current_card_classes = f'{base_classes} {active_width_class} {self._current_background_class}'
    #         current_card_style = self._glass
    #     else:
    #         # When inactive: only base_classes, no max-w, no _glass style (explicitly unset), no background
    #         # Add a margin for cards in the drawer
    #         current_card_classes = f'{base_classes} m-1'  # Added m-1 for margin
    #         # Explicitly unset properties from _glass style when inactive
    #         current_card_style = 'backdrop-filter: none; -webkit-backdrop-filter: none; border-radius: 0; border: none;'
    #         self._current_background_class = ''  # Ensure background is clear when inactive
    #
    #     self.card.classes(replace=current_card_classes.strip())
    #     self.card.style(current_card_style)

    def _handle_activation_change(self):
        if self.timer.active:
            # Show active card
            asyncio.create_task(self.ping())
            self.card.move(self.main_container)
            self.card.classes(replace='w-full sm:max-w-56 break-inside-avoid')  # Add sm:max-w-56 for main container
            self.front.set_visibility(True)
            self.back.set_visibility(False)
            self.title.set_visibility(self.title_checkbox.value)
            self.inactive.set_visibility(False)
        else:
            # Show inactive card
            self.card.move(self.drawer_container)
            self.card.classes(replace='w-full break-inside-avoid mb-30')  # Remove sm:max-w-56 for drawer container
            self.front.set_visibility(False)
            self.back.set_visibility(False)
            self.title.set_visibility(False)
            self.inactive.set_visibility(True)

    def _get_properties(self):
        values = dict(active = self.timer.active,
                      title = self.title.text,
                      target = self.target.text,
                      interval = self.interval,
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
            lambda: subprocess.run(
                ['ping', '-c', '1', target],
                capture_output=True,
                text=True,
                timeout=4
            )
        )

    async def ping(self, target=''):
        if not self.timer.active:
            return  # do nothing when switched off

        if not target:
            target = self.target.text

        # Validate target to prevent command injection and invalid inputs
        if not is_valid_hostname_or_ip(str(target)):
            self.result.set_text('Invalid target')
            self.set_background('bg-yellow-300/20')
            self.target_status_icon.classes(replace='text-yellow')
            return

        try:
            response = await asyncio.wait_for(self.sh_ping(target), timeout=5)
        except asyncio.TimeoutError:
            self.result.set_text('Ping timed out.')
            self.set_background('bg-yellow-300/20')
            self.target_status_icon.classes(replace='text-yellow')
            return
        except Exception:
            self.result.set_text('Ping error')
            self.set_background('bg-red-500/20')
            self.target_status_icon.classes(replace='text-red')
            return

        # Only work with a bounded portion of stdout to avoid excessive processing
        stdout = '\n'.join(response.stdout.splitlines()[-5:])
        match = re.search(r'(\d+)(?: packets)? received', stdout)

        if not match:
            self.result.set_text('Ping error')
            self.set_background('bg-red-500/20')
            self.target_status_icon.classes(replace='text-red')
        else:
            if not int(match.group(1)) > 0:
                self.result.set_text('Red: Ping Failed')
                self.set_background('bg-red-500/20')
                self.target_status_icon.classes(replace='text-red')
            else:
                # Attempt to parse latency safely
                try:
                    line = stdout.splitlines()[-1]
                    numerical_part = line.split('=')[1].strip()
                    parts = numerical_part.replace(' ms', '').split('/')
                except Exception:
                    parts = []

                if parts and len(parts) >= 3:
                    min_val = parts[0]
                    avg_val = parts[1]
                    max_val = parts[2]

                    self.result.set_text(str(avg_val) + ' ms')
                    self.set_background('bg-green-500/20')
                    self.target_status_icon.classes(replace='text-green')
                    self.ping_history.append(avg_val)
                    # Keep only the most recent 100 samples to avoid unbounded growth
                    if len(self.ping_history) > 30:
                        self.ping_history[:] = self.ping_history[-30:]
                    if self.chart_div.visible:
                        self.ping_chart.update()
                else:
                    self.result.set_text('Yellow: Parse error')
                    self.set_background('bg-yellow-300/20')
                    self.target_status_icon.classes(replace='text-yellow')