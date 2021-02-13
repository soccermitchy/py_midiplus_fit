from .Fader import Fader
import rtmidi


class MidiPlus:
    midi_in = rtmidi.MidiIn()
    midi_out = rtmidi.MidiOut()

    faders: 'list[Fader]' = [None] * 17
    callbacks = {}

    button_ids = {
        "LAYER_1": 0x40,
        "LAYER_2": 0x41,
        "LAYER_3": 0x42,
        "LAYER_4": 0x43,
        "LAYER_5": 0x44,
        "LAYER_6": 0x45,
        "LAYER_7": 0x46,
        "LAYER_8": 0x47,
        "UTIL_1": 0x50,
        "UTIL_2": 0x51,
        "UTIL_3": 0x52,
        "UTIL_4": 0x53,
        "UTIL_5": 0x54,
        "UTIL_6": 0x55,
        "UTIL_7": 0x56,
        "UTIL_8": 0x57,
        "TEMPO": 0x58
    }

    def __init__(self, in_port_num: int, out_port_num: int):
        self.midi_in.open_port(in_port_num)
        self.midi_out.open_port(out_port_num)
        for i in range(1, 18):
            self.faders[i-1] = Fader(self, i)
        self.midi_in.set_callback(self.__on_recv, self)

    def __gen_display_header(_):
        return [0xf0, 0x00, 0x00, 0x74, 0x3c, 0x1a, 0x01]

    def __gen_rgb_header(_):
        return [0xf0, 0x00, 0x00, 0x74, 0x3c, 0x1a, 0x03, 0x01, 0x40]

    def raw_write(self, message):
        # print("[" + (" ".join("0x%02x" % b for b in message) + "]"))
        self.midi_out.send_message(message)

    def __on_recv(self, midi_data, _):
        message = midi_data[0]
        command = message[0]
        # print("cmd 0x%02x \t data %s" % (command, (" ".join(
        #     "0x%02x" % b for b in message[1:]))))
        if command == 0x90:  # Button press
            self.__on_btn(message[1:])
        elif (command >= 0xE0 and command <= 0xEF) or command == 0xAF:  # Fader move
            self.__on_fader_move(command, message[1:])
        elif command == 0xb0:
            self.__on_knob_turn(message[1:])

    def __on_btn(self, data):
        button_id = data[0]
        pressed = (data[1] == 0x7f)
        # global buttons (right side)
        if (button_id >= self.button_ids["LAYER_1"] and button_id <= self.button_ids["TEMPO"]):
            if button_id >= self.button_ids["LAYER_1"] and button_id <= self.button_ids["LAYER_8"]:
                layer = button_id - (self.button_ids["LAYER_1"] - 1)
                if pressed:
                    self.fire_callback("layer_press", layer)
                else:
                    self.fire_callback("layer_release", layer)
            if button_id >= self.button_ids["UTIL_1"] and button_id <= self.button_ids["UTIL_8"]:
                layer = button_id - (self.button_ids["UTIL_1"] - 1)
                if pressed:
                    self.fire_callback("util_press", layer)
                else:
                    self.fire_callback("util_release", layer)
            if button_id == self.button_ids["TEMPO"]:
                if pressed:
                    self.fire_callback("tempo_press")
                else:
                    self.fire_callback("tempo_release")
        else:
            for fader in self.faders:
                if button_id == fader.select_btn_id:
                    if pressed:
                        fader.fire_callback("select_press")
                    else:
                        fader.fire_callback("select_release")
                elif button_id == fader.solo_btn_id:
                    if pressed:
                        fader.fire_callback("solo_press")
                    else:
                        fader.fire_callback("solo_release")
                elif button_id == fader.mute_btn_id:
                    if pressed:
                        fader.fire_callback("mute_press")
                    else:
                        fader.fire_callback("mute_release")
                elif button_id == fader.fader_touch_id:
                    if pressed:
                        fader.fire_callback("fader_touch")
                    else:
                        fader.fire_callback("fader_release")
        pass

    def __on_fader_move(self, command, data):
        for fader in self.faders:
            if command == fader.fader_id:
                fader.fire_callback(
                    "fader_move", int.from_bytes(data, 'little'))

    def __on_knob_turn(self, data):
        knob_id = data[0]
        speed = data[1]
        for fader in self.faders:
            if knob_id == fader.knob_id:
                if (speed > 0x40):
                    speed = -(speed - 0x40)
                fader.fire_callback("knob_turn", speed)

    def register_callback(self, name: str, callback):
        self.callbacks[name] = callback

    def fire_callback(self, name, *args):
        if name in self.callbacks:
            self.callbacks[name](self, *args)

    def write_single_row_single_screen(self, screen: int, row: int, text: str):
        # map right-most display to nicer value
        if screen == 17:
            screen = 127
        message = self.__gen_display_header()
        message.append(0x00)
        message.append(0x07)
        message.append(screen)
        message.append(row)
        max_len = 7
        # make sure str ends up as `max_len` chars
        if (len(text) > max_len):
            text = text[0:max_len]
        text = text.ljust(max_len, " ")
        for char in text:
            message.append(ord(char))
        message.append(0xf7)
        self.raw_write(message)

    def write_all_rows_single_screen(self, screen: int, text: str):
        # map right-most display to nicer value
        if screen == 17:
            screen = 127
        message = self.__gen_display_header()
        message.append(0x00)
        message.append(0x07)
        message.append(screen)
        message.append(0x00)
        max_len = 7 * 5
        # make sure str ends up as `max_len` chars
        if (len(text) > max_len):
            text = text[0:max_len]
        text = text.ljust(max_len, " ")
        for char in text:
            message.append(ord(char))
        message.append(0xf7)
        self.raw_write(message)

    def write_single_row_all_screens(self, row: int, text: str):
        message = self.__gen_display_header()
        message.append(0x00)
        message.append(0x07)
        message.append(0x00)
        message.append(row)
        max_len = 7 * 17
        # make sure str ends up as `max_len` chars
        if (len(text) > max_len):
            text = text[0:max_len]
        text = text.ljust(max_len, " ")
        for char in text:
            message.append(ord(char))
        message.append(0xf7)
        self.raw_write(message)

    def write_all_rows_all_screens(self, text: str):
        message = self.__gen_display_header()
        message.append(0x00)
        message.append(0x07)
        message.append(0x00)
        message.append(0x00)
        max_len = 7 * 5 * 17
        # make sure str ends up as `max_len` chars
        if (len(text) > max_len):
            text = text[0:max_len]
        text = text.ljust(max_len, " ")
        for char in text:
            message.append(ord(char))
        message.append(0xf7)
        self.raw_write(message)

    def clear_screens(self):
        self.write_all_rows_all_screens(" " * (7 * 5 * 17))

    def set_led_channel_select(self, channel_num: int, state: bool):
        if channel_num <= 17:  # limit it to prevent setting other LEDs with this function
            note = channel_num - 1
            # map right-most btn to nicer value
            if channel_num == 17:
                note = 0x70
            self.raw_write(
                [0x90, note, (0x7F if state else 0x00)])

    def set_led_channel_solo(self, channel_num: int, state: bool):
        if channel_num <= 17:  # limit it to prevent setting other LEDs with this function
            note = 0x20 + (channel_num - 1)
            # map right-most btn to nicer value
            if channel_num == 17:
                note = 0x72
            self.raw_write(
                [0x90, note, (0x7F if state else 0x00)])

    def set_led_channel_mute(self, channel_num: int, state: bool):
        if channel_num <= 17:  # limit it to prevent setting other LEDs with this function
            note = 0x30 + (channel_num - 1)
            # map right-most btn to nicer value
            if channel_num == 17:
                note = 0x73
            self.raw_write(
                [0x90, note, (0x7F if state else 0x00)])

    def set_led_layer(self, layer_num: int, state: bool):
        note = 0x40 + (layer_num - 1)
        self.raw_write(
            [0x90, note, (0x7F if state else 0x00)])

    def set_led_util(self, util_num: int, state: bool):
        note = 0x50 + (util_num - 1)
        self.raw_write(
            [0x90, note, (0x7F if state else 0x00)])

    def set_led_tempo(self, state: bool):
        self.raw_write(
            [0x90, 0x58, (0x7F if state else 0x00)])

    def set_fader(self, channel_num: int, val: int):
        note = 0xE0 + (channel_num - 1)
        if channel_num == 17:
            note = 0xAF
        message = [note]
        for b in val.to_bytes(2, 'little'):
            message.append(b)
        self.raw_write(message)

    # def set_color_table(self, color_table)