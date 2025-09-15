import re
import subprocess
from nicegui import ui

#--------------------------------------------------------------------
# Write about the attrs here
# self.title            STR
# self.target           STR
# self.interval         INT
# self.timer.active     BOOL
#--------------------------------------------------------------------


class PingCard:
    def __init__(self, target: str, container: ui.element, interval=60):
        # instantiate variables
        self.interval = interval

        # creates timer and performs initial ping
        self.timer = ui.timer(interval=self.interval, callback=lambda: self.ping())

        with container:
            self.card = ui.card().classes('m-2 w-full sm:max-w-56 break-inside-avoid')
            with self.card:
                self.front = ui.card_section().classes('transition')
                with self.front:
                    self.card_front(target)

                self.back = ui.card_section().classes('transition')
                self.back.set_visibility(False)
                with self.back:
                    self.card_back()

    def card_front(self, target: str):
        self.title = ui.label('Ping Card').classes('text-xl font-bold')
        self.target = ui.label(target)
        self.result = ui.label('0ms')
        ui.icon('network_ping').on('click', lambda: self.ping()).classes('m-1 text-xl')
        ui.icon('settings_applications').on('click', self.flip_card).classes('m-1 text-xl')

    def card_back(self):
        with ui.input('Target') as target_input:
            target_input.set_value(self.target.text)
            with target_input.add_slot('append'):
                ui.icon('network_ping').classes('text-red cursor-pointer')

        ui.button(icon='save', on_click=lambda: self.set_target(target_input.value)).classes('m-1 text-xs')
        ui.switch('Timer').bind_value_to(self.timer, 'active').set_value(True)

        with (ui.expansion('Options')):
            title_checkbox = ui.checkbox('Show card title')
            title_checkbox.set_value(True)
            self.title.bind_visibility_from(title_checkbox, 'value')
            ui.button(icon='delete', on_click=self.trash).classes('text-xs bg-red')

        ui.icon('settings_applications').on('click', self.flip_card).classes('m-1 text-xl')

    def flip_card(self):
        if self.front.visible:
            self.front.set_visibility(False)
            self.back.set_visibility(True)
        else:
            self.front.set_visibility(True)
            self.back.set_visibility(False)

    def set_target(self, new_target: str) -> None:
        """Changes the ping target."""
        self.target.set_text(new_target)
        self.ping()

    def trash(self):
        self.timer.cancel()
        self.card.delete()

    def ping(self, target=''):
        if not target:
            target = self.target.text

        response = subprocess.run(['ping', '-c 1', f'{target}'],
                                  capture_output=True,
                                  text=True)

        match = re.search(r'(\d+)\s+received', response.stdout)
        if not match:
            self.result.set_text(response.stderr)
            self.card.classes(replace='bg-red-500')
        else:
            if not int(match.group(1)) > 0:
                self.result.set_text('Red: Ping Failed')
                self.card.classes(replace='bg-red-500')
            else:
                # Regular expression to capture the min/avg/max/mdev values
                match = re.search(
                    r"rtt min/avg/max/mdev = (\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)/(\d+\.\d+)",
                    response.stdout,
                )

                if match:
                    min_val = match.group(1)
                    avg_val = match.group(2)
                    max_val = match.group(3)
                    mdev_val = match.group(4)

                    speed = {
                        'min': min_val,
                        'avg': avg_val,
                        'max': max_val,
                        'mdev': mdev_val
                    }

                    self.result.set_text(speed['avg'] + 'ms')
                    self.card.classes(replace='bg-green-600')
                else:
                    self.result.set_text('Red: String parse error')
                    self.card.classes(replace='bg-red-500')