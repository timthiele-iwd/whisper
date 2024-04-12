import whisper
import time
import librosa
import soundfile as sf
import re
import os
import shutil
from utils.utils import write_to_excel
from pydub import AudioSegment


class Whisper_Handler:
    
    def __init__(self, file_root, language="de", model_size="medium", logger=None):
        if logger is None:
            raise ValueError("Please hand over a logging object")
        self.lh = logger
        self.file_root = file_root
        language_options = ["en", "de"]
        model_size_options = ["tiny", "base", "small", "medium", "large"]
        self.model = whisper.load_model(model_size)
        whisper.DecodingOptions(language=language)
        
        self.folders =  {
            "root": r"WhisperAudio",
            "raw": r"WhisperAudio\FilesToTranscribe",
            "processed": r"WhisperAudio\ProcessedAudio",
            "transcribed": r"WhisperAudio\TextFiles",
        }
        for key, value in self.folders.items():
            self.folders[key] = os.path.join(self.file_root, value)
            os.makedirs(self.folders[key], exist_ok=True)
   

    def transcribe(self):
        
        try:
          audio_folder, processed_folder, text_file_folder = self.folders["raw"], self.folders["processed"], self.folders["transcribed"]
          audio_files, audio_names = [], []

          for file in os.listdir(audio_folder):
            
            file_path = os.path.join(audio_folder, file)
            audio_files.append(file_path)
            audio_names.append(file)
            a = 0

            # TODO: CONVERSION
            """
            if file.endswith(".mp3"):
              audio_files.append(file_path)
              audio_names.append(file)
              continue
            
            else:
              file_extension = file.split('.')[-1].lower()
              format = None
              if file_extension in ['wav', 'm4a', 'ogg', 'flac']:
                  format = file_extension
                  if format == "wav":
                      continue
                  else:
                      source_audio  = AudioSegment.from_file(file_path, format=format)
                  new_source_audio_path = file_path.replace("."+format, ".mp3")
                  source_audio.export(new_source_audio_path, format="mp3")
                  audio_files.append(new_source_audio_path)
                  audio_names.append(file.replace(format, ".mp3"))
                  a = 0
              else:
                  raise ValueError("Audio dtype not converted.")
              """
          
          for f in audio_files:
            self.lh.log(f)

          if len(audio_files) == 0:
            self.lh.log("You have no files.")
            return f"No files found in the specified directory {audio_folder}"

          # Loop through the audio files, split each audio file based on pauses in speech then transcribe them with Whisper.
          for i, file in enumerate(audio_files):
            self.lh.log(f"Processing {audio_names[i]}...")

            # Load the audio file and convert it to 16 kHz mono
            audio, sr = librosa.load(file, sr=16000, mono=True)
            # Detect pauses and split the audio. We use a threshold of -30 dB and a minimum pause length of 0.5 seconds.
            pauses = librosa.effects.split(audio, top_db=30, frame_length=2048, hop_length=128)
            # Transcribe each segment and concatenate the results
            transcription = ""
            for start, end in pauses: # For each segment
              segment = audio[start:end]
              # Save the segment as a temporary wav file
              temp_file = os.path.join(self.file_root, "temp.wav")
              sf.write(temp_file, segment, sr, subtype='PCM_16')
              if os.path.getsize(temp_file) > 10000:
                # Transcribe the segment with Whisper
                if os.path.exists(temp_file):
                  self.lh.log(f"The file '{temp_file}' exists.") # DEBUG CHECK
                temp_audio, sr = librosa.load(temp_file, sr=16000, mono=True)
                result = self.model.transcribe(temp_audio)
                text = result["text"]
                # Append the text to the transcription
                self.lh.log(f"{len(transcription.split(' '))} words processed")
                transcription += text.strip() + " "
                # Delete the temporary file
                os.remove(temp_file)
            # Print the transcription
            self.lh.log(f"Transcription of {audio_names[i]}:\n")
            self.lh.log(transcription)
            self.lh.log("\n")

            # Convert the spaces between sections into paragraph breaks and save the transcription as a txt document in the same folder as MyAudio.
            transcription = re.sub(r"\s\s+", "\n\n", transcription) # Replace multiple spaces with newlines
            text_file = os.path.join(text_file_folder, audio_names[i][:-4] + ".txt") # Create the text file name
            
            # QS valid characters
            encoded_transcription = None
            while encoded_transcription == None:
                encoded_transcription, error_position = self.encode_string(transcription)
                if not error_position is None:
                  transcription = self.replace_character_at_position(transcription, error_position, replacement="?")

            with open(text_file, "w") as f: # Write the transcription to the text file
              f.write(transcription)
            self.lh.log(f"Saved transcription as {text_file}")

            # EXCEL
            data = [{'Filename': audio_names[i], 'Transcription': transcription}]
            excel_path = os.path.join(self.folders["transcribed"], "transcribed.xlsx")
            write_to_excel(excel_path, data)

          # Move the audio files to processed folder
          if not os.path.exists(processed_folder): # Create the folder if it does not exist
            os.mkdir(processed_folder)
          for file in audio_files: # Move each audio file to the processed folder
            shutil.move(file, os.path.join(processed_folder, os.path.basename(file)))
            self.lh.log(f"Moved {file} to {processed_folder}")

        except Exception as e:
            self.lh.log(f"Exception occured: {e}")
            return f"An error occured: {e}"
        
        else:
            return "Successfully transcribed"
        
        
    # === UTIL FUNCTIONS ===
    def encode_string(self, s, encoding='charmap'):
        try:
            # Attempt to encode the string using the specified encoding
            encoded_s = s.encode(encoding)
        except UnicodeEncodeError as e:
            # If a UnicodeEncodeError is encountered, extract the error position
            error_position = e.start  # This gives you the position of the error
            self.lh.log(f"Error encoding character at position {error_position}: {s[error_position]}")
            return None, error_position
        return encoded_s, None

    def replace_character_at_position(self, original_string, position, replacement=''):
        if position < 0 or position >= len(original_string):
            raise ValueError("Position is out of the string's bounds")
        return original_string[:position] + replacement + original_string[position+1:]