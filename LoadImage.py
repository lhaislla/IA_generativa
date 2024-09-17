import google.generativeai as genai
import time

class LoadImage:

    @staticmethod
    def upload_file_to_gemini(file_path):
        try:

            file = genai.upload_file(file_path, mime_type='image/jpeg')
            print(f"Uploaded file '{file.display_name}' as: {file.uri}")
            return file
        except Exception as e:
            print(f"Erro ao dar upload na imagem {file_path}: {e}")
            return None
    
    @staticmethod
    def wait_for_files_active(files):
        """Waits for the given files to be active.

        Some files uploaded to the Gemini API need to be processed before they can be
        used as prompt inputs. The status can be seen by querying the file's "state"
        field.

        This implementation uses a simple blocking polling loop. Production code
        should probably employ a more sophisticated approach.
        """
        print("Waiting for file processing...")
        for name in (file.name for file in files):
            file = genai.get_file(name)
            while file.state.name == "PROCESSING":
                print(".", end="", flush=True)
                time.sleep(30)
                file = genai.get_file(name)
                if file.state.name != "ACTIVE":
                    raise Exception(f"File {file.name} failed to process")
        print("...all files ready")
        print()