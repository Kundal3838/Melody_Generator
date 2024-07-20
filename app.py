import os
import streamlit as st
from melody_generator import MelodyGenerator
from MidiToMp3Converter import MidiToMp3Converter

# Set page configuration
st.set_page_config(
    page_title="Project",
    page_icon="🤣"
)



def main():
    st.title("🎵Melody Generator🎵")

    # Add some vertical space between the title and the button
    st.write("")

    # Create an instance of MelodyGenerator
    generator = MelodyGenerator(
        model_path="Model_1",  #change where the Model is located.
        kern_files_directory="kern file_1" # change where the .krn files are located.
    )

    # Add some more vertical space
    st.write("")

    # Add a button to trigger melody generation
    generate_button = st.button("Generate Melody")

    if generate_button:
        # Display loading message
        with st.spinner("Generating melody..."):
            # Generate melody
            generated_melody = generator.generate_melody()

            # Save the generated melody as a MIDI file
            output_file_path = "OUTPUT.mid" # change the path where you want to save the op.
            generated_melody.write('midi', fp=output_file_path)

            # Convert MIDI to MP3
            converter = MidiToMp3Converter()
            mp3_output_path = "output.mp3"
            converter.generate_audio_from_midi(output_file_path, mp3_output_path)

        # Add some vertical space
        st.write("")

        # Display the generated melody
        st.write("Melody generated successfully!")

        # # Open the directory containing the generated MIDI file
        # st.write("Click the button below to open the directory containing the generated MIDI file:")
        # if st.button("Open MIDI File Directory"):
        #     midi_dir_path = os.path.dirname(output_file_path)
        #     os.system(f"explorer /select, {midi_dir_path}")

        # Add an audio player to listen to the generated melody
        st.audio(mp3_output_path, format='audio/mp3')


if __name__ == "__main__":
    main()

st.sidebar.success("Select a page above.")
