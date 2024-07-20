import os
import numpy as np
import tensorflow as tf
from music21 import converter, note, chord, stream
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense
from tensorflow.keras.optimizers import Adam
from tensorflow.keras import backend as K


# Set memory growth for GPU devices
gpus = tf.config.list_physical_devices('GPU')
if gpus:
    tf.config.experimental.set_memory_growth(gpus[0], True)


class MelodyGenerator:
    def __init__(self, model_path, kern_files_directory):
        # Load the trained model
        self.model = tf.keras.models.load_model(model_path)
        
        # Load the musical notes
        self.notes = []
        for file in os.listdir(kern_files_directory):
            midi = converter.parse(os.path.join(kern_files_directory, file))
            notes_to_parse = midi.flat.notes
            for element in notes_to_parse:
                if isinstance(element, note.Note):
                    self.notes.append(str(element.pitch))
                elif isinstance(element, chord.Chord):
                    self.notes.append('.'.join(str(n) for n in element.normalOrder))
        
        # Create dictionaries for note-to-int and int-to-note mappings
        unique_notes = sorted(set(self.notes))
        self.note_to_int = {note: number for number, note in enumerate(unique_notes)}
        self.int_to_note = {number: note for number, note in enumerate(unique_notes)}

    def generate_melody(self, sequence_length=100):
        # Generate a seed sequence
        start = np.random.randint(0, len(self.notes) - sequence_length - 1)
        pattern = [self.note_to_int[note] for note in self.notes[start:start + sequence_length]]

        # Generate notes
        prediction_output = []
        for note_index in range(500):  # Generate 500 notes
            prediction_input = np.reshape(pattern, (1, len(pattern), 1))
            prediction_input = prediction_input / float(len(self.note_to_int))

            prediction = self.model.predict(prediction_input, verbose=0)

            # Sample the index of the next note based on the prediction
            index = np.argmax(prediction)

            result = self.int_to_note[index]

            # Append the predicted note to the output
            prediction_output.append(result)

            # Update the pattern with the new note
            pattern.append(index)
            pattern = pattern[1:]


            # Clear TensorFlow session to free up GPU memory
            K.clear_session()

        # Convert the output to a stream of Note objects
        output_notes = []
        for pattern in prediction_output:
            if '.' in pattern or pattern.isdigit():  # If pattern is a chord
                notes_in_chord = pattern.split('.')
                notes = [note.Note(self.int_to_note[int(note_in_chord)]) for note_in_chord in notes_in_chord]
                chord_note = chord.Chord(notes)
                chord_note.duration.quarterLength = 0.5  # Adjust duration if needed
                output_notes.append(chord_note)
            else:  # If pattern is a single note
                new_note = note.Note(pattern)
                new_note.duration.quarterLength = 0.5  # Adjust duration if needed
                output_notes.append(new_note)

        # Create a stream object and add notes to it
        midi_stream = stream.Stream(output_notes)
        return midi_stream
