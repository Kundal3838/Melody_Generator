from collections import defaultdict
from mido import MidiFile
from pydub import AudioSegment
from pydub.generators import Sine

class MidiToMp3Converter:
    def __init__(self, concert_A=440.0, tempo=100):
        self.concert_A = concert_A
        self.tempo = tempo

    def note_to_freq(self, note):
        '''
        from wikipedia: http://en.wikipedia.org/wiki/MIDI_Tuning_Standard#Frequency_values
        '''
        return (2.0 ** ((note - 69) / 12.0)) * self.concert_A

    def ticks_to_ms(self, ticks, ticks_per_beat):
        if ticks_per_beat == 0:
            return 0
        return (60000.0 / self.tempo) / ticks_per_beat * ticks

    def generate_audio_from_midi(self, midi_file_path, output_file_path):
        mid = MidiFile(midi_file_path)
        output = AudioSegment.silent(int(mid.length * 1000.0))

        if mid.ticks_per_beat == 0:
            print("Error: ticks_per_beat is zero.")
            return

        for track in mid.tracks:
            current_pos = 0.0
            current_notes = defaultdict(dict)

            for msg in track:
                current_pos += self.ticks_to_ms(msg.time, mid.ticks_per_beat)

                if msg.type == 'note_on':
                    current_notes[msg.channel][msg.note] = (current_pos, msg)

                if msg.type == 'note_off':
                    start_pos, start_msg = current_notes[msg.channel].pop(msg.note)
                    duration = current_pos - start_pos
                    signal_generator = Sine(self.note_to_freq(msg.note))

                    # Adjust volume and fade effects
                    rendered = (
                        signal_generator
                        .to_audio_segment(duration=duration, volume=-6)
                        .fade_out(30)
                        .fade_in(30)
                        .apply_gain(-10)  # Adjust volume
                    )

                    output = output.overlay(rendered, start_pos)

        # Add reverb effect
        reverb_effect = output.apply_gain(-6).pan(-0.5)  # Create a copy, delay, and reduce volume
        output = output + reverb_effect

        # Export as mp3 with higher bitrate for better quality
        output.export(output_file_path, format="mp3", bitrate="320k")

# # Usage:
# converter = MidiToMp3Converter()
# converter.generate_audio_from_midi('input.mid', 'output.mp3')
