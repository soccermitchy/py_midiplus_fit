import time
import rtmidi
from .MidiPlus import MidiPlus


def main():
    # Port name we are looking for
    port_name = "FIT"
    in_port_num = -1
    out_port_num = -1

    midiin = rtmidi.MidiIn()
    available_ports = midiin.get_ports()
    for idx, name in enumerate(available_ports):
        if name[0:len(port_name)] == port_name:
            in_port_num = idx

    midiout = rtmidi.MidiOut()
    available_ports = midiout.get_ports()
    for idx, name in enumerate(available_ports):
        if name[0:len(port_name)] == port_name:
            out_port_num = idx

    if in_port_num == -1:
        raise BaseException("could not find midi in device")
    if out_port_num == -1:
        raise BaseException("could not find midi out device")

    mp = MidiPlus(in_port_num, out_port_num)
    mp.clear_screens()
    for fader in mp.faders:
        fader.register_callback("fader_move", lambda self, pos:
                                self.set_row(1, str(pos)))
        fader.register_callback("knob_turn", lambda self, speed:
                                self.set_row(3, str(speed)))
        fader.register_callback("fader_touch", lambda self:
                                self.set_row(5, "FTouch"))
        fader.register_callback("fader_release", lambda self:
                                self.set_row(5, ""))
        fader.register_callback("select_press", lambda self:
                                self.set_led_select(True))
        fader.register_callback("select_release", lambda self:
                                self.set_led_select(False))
        fader.register_callback("solo_press", lambda self:
                                self.set_led_solo(True))
        fader.register_callback("solo_release", lambda self:
                                self.set_led_solo(False))
        fader.register_callback("mute_press", lambda self:
                                self.set_led_mute(True))
        fader.register_callback("mute_release", lambda self:
                                self.set_led_mute(False))
        fader.register_callback("knob_press", lambda self:
                                self.set_row(4, "KPress"))
        fader.register_callback("knob_release", lambda self:
                                self.set_row(4, ""))
    mp.register_callback("layer_press", lambda self, layer:
                         self.set_led_layer(layer, True))
    mp.register_callback("layer_release", lambda self, layer:
                         self.set_led_layer(layer, False))
    mp.register_callback("util_press", lambda self, util:
                         self.set_led_util(util, True))
    mp.register_callback("util_release", lambda self, util:
                         self.set_led_util(util, False))
    mp.register_callback("tempo_press", lambda self:
                         self.set_led_tempo(True))
    mp.register_callback("tempo_release", lambda self:
                         self.set_led_tempo(False))
    mp.clear_screens()

    while True:
        time.sleep(1)
