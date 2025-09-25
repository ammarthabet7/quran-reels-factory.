#  The Agentic Qur'an Reels Factory

A fully autonomous, "fire-and-forget" system to generate hundreds of high-quality, short-form Qur'an videos for social media using local AI.

---

###  Features

-   **Fully Automated:** Run a single command to generate a large batch of unique videos.
-   **Local & Free:** Powered by Ollama, the entire creative process runs on your machine at no cost.
-   **Customizable Reciters:** Easily switch between different famous Qur'an reciters.
-   **High-Quality Output:** Creates 9:16 vertical videos perfect for TikTok, YouTube Shorts, and Instagram Reels.
-   **Smart Memory:** The system logs used verses to ensure it never creates duplicate content.

---

###   Demo

You can check my Tiktok account : https://www.tiktok.com/@w_zakker__
---

###  Project Structure

Your scripts will automatically create the necessary output folders. You only need to create the `data` folder manually.

```
.
├── data/                  <-- You create this folder
│   └── quran-uthmani.xml  <-- Place the Qur'an data file here
├── backgrounds/           <-- Populated by download_backgrounds.py
├── output/                <-- Final videos are saved here
├── logs/                  <-- Tracks used verses
├── temp/                  <-- Caches audio files and other temp data
├── download_backgrounds.py
└── make_videos.py
```

---

###  Prerequisites

Before you begin, make sure you have the following installed and configured:

1.  **Python 3.8+**
2.  **FFmpeg:** It must be installed and accessible from your system's PATH. [Download FFmpeg](https://ffmpeg.org/download.html).
3.  **Ollama:** You need the Ollama server running locally. [Download Ollama](https://ollama.com/).
    -   After installing, pull the model this project uses by running:
        ```bash
        ollama run qwen2:7b
        ```
4.  **Pexels API Key:** To download high-quality background videos legally.
    -   Get your free API key from the [Pexels website](https://www.pexels.com/api/).

---

###  Setup & Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    ```

2.  **Create the `data` folder** and place the `quran-uthmani.xml` file inside.
    -   You can download the file from [tanzil.net](http://tanzil.net/xml/quran-uthmani.xml).

3.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure the scripts:**
    -   Open `download_backgrounds.py` and set your `PEXELS_API_KEY`.
    -   Open `make_videos.py` and review the settings in the **CONFIGURATION** section at the top (like `TOTAL_VIDEOS`, `CHOSEN_RECITER`, etc.).

---

###  How to Use

The factory operates in two simple steps:

#### Step 1: Stock the Warehouse (Download Backgrounds)

Run the background harvester to download a collection of videos. You only need to do this once in a while to get fresh content.

```bash
python download_backgrounds.py
```
This will fill the `backgrounds/` folder with royalty-free videos.

#### Step 2: Start the Factory (Generate Videos)

Run the main script to start the video production line.

```bash
python make_videos.py
```
The script will begin generating videos and saving them in the `output/` folder. Sit back and watch it work!

---

###  Configuration

You can easily customize the factory's output by changing the variables at the top of `make_videos.py`:

-   `TOTAL_VIDEOS`: The number of videos to create in one run.
-   `MODEL_NAME`: The Ollama model to use for creative generation.
-   `RECITERS`: A dictionary where you can add or remove Qur'an reciters.
-   `CHOSEN_RECITER`: The key of the reciter you want to use for the current batch.

---
