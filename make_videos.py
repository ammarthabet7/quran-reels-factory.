import os
import json
import random
import subprocess
import time
import xml.etree.ElementTree as ET
import requests

# --- CONFIGURATION ---
TOTAL_VIDEOS = 100
MODEL_NAME = "qwen3:8b"  

# --- File & Folder Paths ---
QURAN_FILE = os.path.join("data", "quran-uthmani.xml")
BACKGROUNDS_FOLDER = "backgrounds"
OUTPUT_FOLDER = "output"
LOGS_FOLDER = "logs"
USED_VERSES_LOG = os.path.join(LOGS_FOLDER, "used_verses.txt")
TEMP_FOLDER = "temp" # For temporary audio and subtitle files
YOUR_TIKTOK_HANDLE = "@wzakk_er"
RECITERS = {
    "Alafasy": "Alafasy_128kbps",
    "Al-Husary": "Husary_128kbps",
    "Al-Minshawi": "Minshawy_Mujawwad_192kbps",
    "Basfar": "Abdullah_Basfar_192kbps"
}

# --- CHOOSE YOUR RECITER HERE ---
CHOSEN_RECITER = "Alafasy"

# --- AI Prompt ---
AI_PROMPT = """
You are a poetic storyteller and a student of Qur'anic Tafsir (exegesis). Your mission is to unearth profound, visually striking, or deeply emotional themes from the Qur'an that would captivate a social media audience. Avoid simple, overused one-word themes.

For your next video, generate a unique concept by following these steps:
1. Identify a theme that is either a powerful story, a stunning visual from nature, or a deep human emotion described in the Qur'an.
2. Find 1 to 4 consecutive verses that are the heart of this theme.
3. Provide the Surah number, start Ayah, and end Ayah for these verses.
4. Craft a short, poetic, and engaging TikTok title in Arabic.
5. Generate 8 relevant Arabic hashtags that capture the essence of the video.
6. The video must range between 20-40 seconds without any cuts in the ayat.

VERY IMPORTANT: Do not use any verses you have been asked about before. Be unique every time.

Your final output MUST be a single, clean JSON object, with no other text before or after.
Example format:
{
  "theme": "The story of the companions of the cave (Ashab al-Kahf)",
  "surah": 18,
  "start_ayah": 13,
  "end_ayah": 14,
  "title": "قصة الفتية الذين آمنوا بربهم وزدناهم هدى",
  "hashtags": ["#الكهف", "#قصص_القران", "#قران", "#ثبات", "#تلاوة_خاشعة", "#wzakk_er", "#islamic", "#quran"]
}
"""



def setup_environment():
    for folder in [OUTPUT_FOLDER, LOGS_FOLDER, TEMP_FOLDER]:
        if not os.path.exists(folder):
            print(f" Creating folder: {folder}")
            os.makedirs(folder)
            
    if not os.path.exists(USED_VERSES_LOG):
        print(f" Creating log file: {USED_VERSES_LOG}")
        with open(USED_VERSES_LOG, 'w') as f:
            pass # This creates an empty file
        

def get_used_verses():
    with open(USED_VERSES_LOG, 'r', encoding='utf-8') as f:
        return {line.strip() for line in f}


def get_ai_plan(used_verses_set):
    """
    Connects to the local Ollama AI to get a unique video plan.
    """    
    # We will try up to 5 times to get a unique plan from the AI
    for _ in range(5): 
        try:
            # The data we send to the Ollama API endpoint
            payload = {
                "model": MODEL_NAME,
                "format": "json",  
                "prompt": AI_PROMPT,
                "stream": False
            }
            
            # Sending the request to the local server Ollama runs
            response = requests.post("http://localhost:11434/api/generate", json=payload)
            response.raise_for_status()

            # The AI's response is a JSON string within a larger JSON object.
            raw_response_data = response.json()
            json_string_from_ai = raw_response_data['response']
            plan = json.loads(json_string_from_ai)

            #Check if we've used these verses before
            verse_id = f"{plan['surah']}:{plan['start_ayah']}-{plan['end_ayah']}"
            if verse_id not in used_verses_set:
                return plan
            else:
                print(f" AI suggested a used verse ({verse_id}). Asking again...")
               

        except requests.exceptions.RequestException as e:
            print(f" Network Error: Could not connect to Ollama server at http://localhost:11434.")

            return None 

    print("❌ AI failed to provide a unique plan after 5 attempts. Stopping.")
    return None


def get_quran_text(surah_num, start_ayah, end_ayah):
    """
    Parses the local Qur'an XML file to retrieve the text for the specified verses.

    """
    try:
        # Load the XML file into a parsable tree structure
        tree = ET.parse(QURAN_FILE)
        root = tree.getroot()
        
        verses = []
        # Find the specific Surah element by its 'index' attribute
        surah_element = root.find(f"./sura[@index='{surah_num}']")
        if surah_element is None:
            print(f"AI Hallucination")
            return None, None
            
        surah_name = surah_element.get('name')
        
        # --- NEW: Defensive check against AI hallucinations ---
        # Get the total number of verses in this Surah
        total_ayat_in_surah = len(surah_element.findall('aya'))
        if end_ayah > total_ayat_in_surah:
            print(f" AI Hallucination: AI requested Ayah {end_ayah}, but Surah {surah_num} only has {total_ayat_in_surah} verses.")
            return None, None


        # Loop from the start to the end Ayah number
        for ayah_num in range(start_ayah, end_ayah + 1):
            # Find the specific Ayah element within that Surah
            ayah_element = surah_element.find(f"./aya[@index='{ayah_num}']")
            if ayah_element is not None:
                verses.append(ayah_element.get('text'))
            else:
                # This part is now less likely to be needed
                print(f" Error: Could not find Ayah {ayah_num} in Surah {surah_num} even though it should exist.")
                return None, None
        
        return verses, surah_name

    except FileNotFoundError:
        print(f" Critical Error: The Qur'an file '{QURAN_FILE}' was not found.")
        return None, None

def run_command(command):
    """
    A helper function to run external commands (like ffprobe/ffmpeg) reliably.
    """
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True, encoding='utf-8')
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f" Error running command: {' '.join(command)}")
        print(f"   Error message: {e.stderr.strip()}")
        return None
    except FileNotFoundError:
        print(f" Error: The command '{command[0]}' was not found.")
        print("   Please ensure FFmpeg is installed and in your system's PATH.")
        return None

def get_audio_duration(file_path):
    """
    Uses ffprobe to get the precise duration of an audio or video file in seconds.
    """
    command = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        str(file_path)
    ]
    duration_str = run_command(command)
    if duration_str:
        return float(duration_str)
    return 0.0


def download_and_prepare_audio(surah_num, start_ayah, end_ayah, reciter_id): 

    audio_cache_folder = os.path.join(TEMP_FOLDER, "audio_cache")
    os.makedirs(audio_cache_folder, exist_ok=True)

    individual_audio_files = []
    ayah_durations = []

    for ayah_num in range(start_ayah, end_ayah + 1):
        # This is the filename from the website
        url_file_name = f"{str(surah_num).zfill(3)}{str(ayah_num).zfill(3)}.mp3"
        
        # --- The cached file includes the reciter's ID ---
        cached_file_name = f"{reciter_id}_{surah_num}_{ayah_num}.mp3"
        file_path = os.path.join(audio_cache_folder, cached_file_name)
        
        individual_audio_files.append(file_path)

        if not os.path.exists(file_path):
            print(f"   Downloading audio for {surah_num}:{ayah_num}...")
            # ---The URL is  dynamic based on the chosen reciter ---
            url = f"https://everyayah.com/data/{reciter_id}/{url_file_name}"
            try:
                response = requests.get(url, stream=True)
                response.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
            except requests.exceptions.RequestException as e:
                print(f"Failed to download audio for {surah_num}:{ayah_num}. Error: {e}")
                return None, None
        
        duration = get_audio_duration(file_path)
        if duration == 0.0:
            return None, None
        ayah_durations.append(duration)

    combined_audio_path = os.path.join(TEMP_FOLDER, "combined_audio.mp3")
    concat_list_path = os.path.join(TEMP_FOLDER, "concat_list.txt")

    with open(concat_list_path, 'w', encoding='utf-8') as f:
        for audio_file in individual_audio_files:
            f.write(f"file '{os.path.abspath(audio_file).replace(os.sep, '/')}'\n")

    command = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list_path,
        "-c", "copy", combined_audio_path
    ]
    
    if run_command(command) is None:
        print(" Failed to concatenate audio files.")
        return None, None

    print(" Audio gathered and prepared successfully.")
    return combined_audio_path, ayah_durations
 

def adapt_plan_duration(verses, durations, end_ayah, min_dur, max_dur):

    current_verses = list(verses)
    current_durations = list(durations)
    current_end_ayah = end_ayah
    total_duration = sum(current_durations)
    
    while total_duration > max_dur and len(current_verses) > 1:
        print(f"Duration ({total_duration:.1f}s) is too long. Trimming last Ayah.")
        current_verses.pop()
        current_durations.pop()
        current_end_ayah -= 1
        total_duration = sum(current_durations)
        
    if total_duration < min_dur:
        print(f"Quality Check Failed: Salvaged duration ({total_duration:.1f}s) is too short. Skipping.")
        return None, None, None
        
    print(f" Plan adapted. Final duration: {total_duration:.1f}s")
    return current_verses, current_durations, current_end_ayah



def render_video(video_number, ai_plan, backgrounds_list, audio_path, total_audio_duration):

    
    background_path = random.choice(backgrounds_list)
    print(f"   - Using background: {os.path.basename(background_path)}")
    
    video_path = os.path.join(OUTPUT_FOLDER, f"video_{str(video_number).zfill(3)}.mp4")

    # Define a simple video filter for resizing and color correction.
    video_filter = (
        "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        "eq=contrast=1.05:saturation=1.1"
    )
    
    # Construct the simplified FFmpeg command.
    command = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", background_path,
        "-i", audio_path,
        "-map", "0:v", "-map", "1:a",
        "-vf", video_filter,  
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-t", str(total_audio_duration),
        "-movflags", "+faststart",
        video_path
    ]
    
    print(" Rendering with FFmpeg ")
    if run_command(command) is None:
        print(" Video rendering failed.")
        return False


    print(f" Video successfully rendered: {video_path}")
    return True




def main():

    setup_environment()
    
    reciter_id = RECITERS[CHOSEN_RECITER]

    used_verses = get_used_verses()
    
    try:
        backgrounds_list = [os.path.join(BACKGROUNDS_FOLDER, f) for f in os.listdir(BACKGROUNDS_FOLDER) if f.endswith(".mp4")]
        if not backgrounds_list:
            print(" The 'backgrounds' folder is empty. Please add videos.")
            return
    except FileNotFoundError:
        print(f" The '{BACKGROUNDS_FOLDER}' folder was not found.")
        return

    videos_created = 0
    for i in range(1, TOTAL_VIDEOS + 1):
        if videos_created >= TOTAL_VIDEOS: break
        print(f"\n--- Starting Video {i}/{TOTAL_VIDEOS} ---")
        
        ai_plan = get_ai_plan(used_verses)
        if not ai_plan: continue

        verses, surah_name = get_quran_text(ai_plan['surah'], ai_plan['start_ayah'], ai_plan['end_ayah'])
        if not verses: continue

        # --- Pass the reciter_id to the audio function ---
        audio_path, durations = download_and_prepare_audio(
            ai_plan['surah'], ai_plan['start_ayah'], ai_plan['end_ayah'], reciter_id
        )
        if not audio_path: continue
            
        adapted_verses, adapted_durations, adapted_end_ayah = adapt_plan_duration(
            verses, durations, ai_plan['end_ayah'], 7, 30
        )
        if not adapted_verses: continue
        final_duration = sum(adapted_durations)
        
        success = render_video(i, ai_plan, backgrounds_list, audio_path, final_duration)
        
        if success:
            verse_id = f"{ai_plan['surah']}:{ai_plan['start_ayah']}-{adapted_end_ayah}"
            with open(USED_VERSES_LOG, 'a', encoding='utf-8') as f: f.write(f"{verse_id}\n")
            used_verses.add(verse_id)
            videos_created += 1
            print("   - Pausing for a moment...")
            time.sleep(2)

    print(f"\n Production Run Complete ---")
    print(f"--- Created {videos_created} videos in the '{OUTPUT_FOLDER}' folder. ---")


if __name__ == "__main__":
    main()