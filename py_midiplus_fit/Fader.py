
class Fader:
    controller = None
    channel: int = None
    select_btn_id: int = None
    solo_btn_id: int = None
    mute_btn_id: int = None
    fader_touch_id: int = None
    fader_id: int = None

    def __init__(self, controller, channel: int):
        self.controller = controller
        self.channel = channel
        # Init IDs for everything
        self.select_btn_id = channel - 1
        self.knob_id = self.select_btn_id + 0x10
        self.solo_btn_id = self.select_btn_id + 0x20
        self.mute_btn_id = self.select_btn_id + 0x30
        self.fader_touch_id = self.select_btn_id + 0x60
        self.fader_id = self.select_btn_id + 0xE0
        self.callbacks = {}
        if channel == 17:  # Whee, special cases!
            self.select_btn_id = 0x70
            self.knob_id = 0x71
            self.solo_btn_id = 0x72
            self.mute_btn_id = 0x73
            self.fader_touch_id = 0x7F
            self.fader_id = 0xAF

    def set_row(self, row: int, text: str):
        self.controller.write_single_row_single_screen(self.channel, row, text)

    def set_all(self, text: str):
        self.controller.write_all_rows_single_screen(self.channel, text)

    def set_fader(self, val: int):
        self.controller.set_fader(self.channel, val)

    def set_led_select(self, state: bool):
        self.controller.set_led_channel_select(self.channel, state)

    def set_led_solo(self, state: bool):
        self.controller.set_led_channel_solo(self.channel, state)

    def set_led_mute(self, state: bool):
        self.controller.set_led_channel_mute(self.channel, state)

    def register_callback(self, name: str, callback):
        self.callbacks[name] = callback

    def fire_callback(self, name, *args):
        if name in self.callbacks:
            self.callbacks[name](self, *args)
