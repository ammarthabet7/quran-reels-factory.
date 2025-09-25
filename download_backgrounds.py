import os
import requests
from tqdm import tqdm

# CONFIGURATION

API_KEY = 
#SEARCH_QUERIES = ["nature", "ocean waves", "calm sky", "forest rain", "mountains", "clouds timelapse"]
SEARCH_QUERIES = ["Islam", "muslims", "mousque", "kaaba"]

DOWNLOAD_FOLDER = "backgrounds"
LOGS_FOLDER = "logs"
DOWNLOAD_LOG_FILE = os.path.join(LOGS_FOLDER, "downloaded_ids.txt")
VIDEOS_TO_DOWNLOAD_PER_RUN = 100

PEXELS_SEARCH_URL = "https://api.pexels.com/videos/search"


def setup():

    if not os.path.exists(DOWNLOAD_FOLDER):
        print(f"Creating folder: {DOWNLOAD_FOLDER}")
        os.makedirs(DOWNLOAD_FOLDER)
    if not os.path.exists(LOGS_FOLDER):
        print(f"Creating folder: {LOGS_FOLDER}")
        os.makedirs(LOGS_FOLDER)
    if not os.path.exists(DOWNLOAD_LOG_FILE):
        print(f"Creating log file: {DOWNLOAD_LOG_FILE}")
        with open(DOWNLOAD_LOG_FILE, 'w') as f:
            pass 
        

def get_downloaded_ids():
 
    with open(DOWNLOAD_LOG_FILE, 'r') as f:
        return {line.strip() for line in f}
    


def download_video(url, filename):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    block_size = 1024  

    with open(filename, 'wb') as f, tqdm(
        total=total_size, unit='iB', unit_scale=True, desc=os.path.basename(filename)
    ) as pbar:
        for data in response.iter_content(block_size):
            pbar.update(len(data))
            f.write(data)

def log_downloaded_id(video_id):

    with open(DOWNLOAD_LOG_FILE, 'a') as f:
        f.write(f"{video_id}\n")

def main():

    setup()
    downloaded_ids = get_downloaded_ids()
    headers = {"Authorization": API_KEY}
    
    videos_found_this_run = 0
    page = 1
    
    print(" Searching for new background videos...")

    while videos_found_this_run < VIDEOS_TO_DOWNLOAD_PER_RUN:
        found_new_on_this_page = False
        for query in SEARCH_QUERIES:
            if videos_found_this_run >= VIDEOS_TO_DOWNLOAD_PER_RUN:
                break
            
            params = {
                "query": query,
                "orientation": "portrait",
                "per_page": 20, # Ask for 20 results at a time
                "page": page
            }
            
            response = requests.get(PEXELS_SEARCH_URL, headers=headers, params=params)

            if response.status_code != 200:
                print(f"\n Error fetching '{query}': {response.status_code} - {response.text}")
                continue

            data = response.json()
            
            for video in data.get("videos", []):
                video_id = str(video['id'])
                if video_id in downloaded_ids:
                    continue 

                # Find the best quality vertical file (1080x1920)
                best_file = next((f for f in video['video_files'] if f.get('width') == 1080), None)

                if best_file:
                    found_new_on_this_page = True
                    file_path = os.path.join(DOWNLOAD_FOLDER, f"pexels_{video_id}.mp4")
                    
                    print(f"\n Found new video: '{query}' (ID: {video_id})")
                    download_video(best_file['link'], file_path)
                    
                    log_downloaded_id(video_id)
                    downloaded_ids.add(video_id)
                    videos_found_this_run += 1

                    if videos_found_this_run >= VIDEOS_TO_DOWNLOAD_PER_RUN:
                        break
        
        page += 1
        if not found_new_on_this_page and not data.get('next_page'):
            print("\nNo more new videos found for the current search terms.")
            break
            
    print(f"\n Downloading is finished {videos_found_this_run} new videos.")


if __name__ == "__main__":

    main()