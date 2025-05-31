import streamlit as st
import yt_dlp
import os
import re

# Initialize session state for theme
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'light'

def is_valid_youtube_url(url):
    pattern = r'^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[\w-]{11}($|&|\?)'
    return bool(re.match(pattern, url.strip()))

def get_video_info(url):
    try:
        ydl_opts = {'quiet': True, 'skip_download': True, 'forcejson': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        formats = [f for f in info['formats'] if f.get('vcodec') != 'none' and f.get('acodec') != 'none' and f.get('ext') == 'mp4']
        available_qualities = sorted(set(f['format_note'] for f in formats if 'format_note' in f), reverse=True)
        return {
            'title': info.get('title'),
            'uploader': info.get('uploader'),
            'duration': info.get('duration_string', ''),
            'thumbnail': info.get('thumbnail'),
            'formats': formats,
            'available_qualities': available_qualities
        }
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def download_video(url, format_id, download_path):
    try:
        os.makedirs(download_path, exist_ok=True)
        ydl_opts = {
            'format': format_id,
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'quiet': False,
            'noprogress': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url)
        return info.get('title')
    except Exception as e:
        st.error(f"Download failed: {e}")
        return None

# Page configuration
st.set_page_config(
    page_title="YouTube Video Downloader",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremely.com/help',
        'Report a bug': "https://www.extremely.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Roboto', sans-serif;
    }

    .stApp {
        background-color: var(--background-color);
        color: var(--text-color);
    }

    .st-emotion-cache-10trblm { /* Main content area */
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    h1 {
        color: var(--primary-color);
        text-align: center;
        font-weight: 700;
        margin-bottom: 1.5rem;
    }

    h2, h3, h4, h5, h6 {
        color: var(--primary-color);
    }

    .stTextInput > div > div > input {
        border-radius: 0.5rem;
        border: 1px solid var(--border-color);
        padding: 0.75rem 1rem;
    }

    .stButton > button {
        border-radius: 0.5rem;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.2s ease-in-out;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
    }

    .stSelectbox > div > div {
        border-radius: 0.5rem;
        border: 1px solid var(--border-color);
    }

    .stExpander {
        border-radius: 0.5rem;
        border: 1px solid var(--border-color);
        padding: 1rem;
        background-color: var(--secondary-background-color);
    }

    .stExpander > div > div > p {
        font-size: 0.9rem;
        line-height: 1.5;
    }

    .footer {
        text-align: center;
        margin-top: 3rem;
        font-size: 0.85rem;
        color: var(--text-color-light);
    }

    /* Theme specific variables */
    :root {
        --primary-color: #FF4B4B; /* Streamlit's default primary */
        --background-color: #FFFFFF;
        --secondary-background-color: #F0F2F6;
        --text-color: #333333;
        --text-color-light: #666666;
        --border-color: #DDDDDD;
    }

    [data-theme="dark"] {
        --primary-color: #FF4B4B;
        --background-color: #1E1E1E;
        --secondary-background-color: #2D2D2D;
        --text-color: #E0E0E0;
        --text-color-light: #AAAAAA;
        --border-color: #444444;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar
with st.sidebar:
    st.header("App Navigation")
    st.button("Home", use_container_width=True)
    st.button("About", use_container_width=True)
    st.button("Settings", use_container_width=True)

    st.markdown("---")
    st.subheader("Theme Settings")
    # Theme toggle using a checkbox for a more modern look
    dark_mode = st.checkbox("Enable Dark Mode", value=(st.session_state['theme'] == 'dark'))
    st.session_state['theme'] = 'dark' if dark_mode else 'light'

# Main content
st.markdown("<h1 style='text-align: center; color: var(--primary-color);'>🎥 YouTube Video Downloader</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: var(--text-color-light); margin-top: -1rem; margin-bottom: 2rem;'>Powered by yt-dlp</p>", unsafe_allow_html=True)

url = st.text_input("Enter YouTube Video URL", placeholder="e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ", help="Paste the full YouTube video URL here.")

if url:
    if not is_valid_youtube_url(url):
        st.error("🚫 Please enter a valid YouTube video URL.")
    else:
        with st.spinner("Fetching video information..."):
            video_info = get_video_info(url)
        
        if video_info:
            st.success("Video information fetched successfully!")
            st.markdown("---")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                if video_info['thumbnail']:
                    st.image(video_info['thumbnail'], use_column_width=True, caption="Video Thumbnail")
            with col2:
                st.subheader(video_info['title'])
                st.markdown(f"👤 **Channel:** {video_info['uploader']}")
                st.markdown(f"⏱️ **Duration:** {video_info['duration']}")
                
                if video_info['available_qualities']:
                    quality = st.selectbox("Select Video Quality", video_info['available_qualities'], help="Choose the desired video resolution.")
                    format_choices = [f for f in video_info['formats'] if f.get('format_note') == quality]
                    format_id = format_choices[0]['format_id'] if format_choices else 'best'
                    
                    st.markdown("---")
                    if st.button("⬇️ Download Video", type="primary", use_container_width=True):
                        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
                        with st.spinner(f"Downloading '{video_info['title']}'..."):
                            title = download_video(url, format_id, downloads_path)
                        if title:
                            st.success(f"✅ Video '{title}' downloaded to your Downloads folder.")
                        else:
                            st.error("❌ Video download failed.")
                else:
                    st.warning("⚠️ No downloadable formats found for this video.")
        else:
            st.error("Could not retrieve video information. Please check the URL or try again later.")

st.markdown("---")
with st.expander("💡 How to use this app"):
    st.markdown(
        """
        1.  **Paste a YouTube Video URL:** Copy and paste the full URL of the YouTube video you want to download into the input box above.
        2.  **Fetch Video Info:** The app will automatically fetch and display details like the video title, channel, duration, and thumbnail.
        3.  **Select Quality:** Choose your preferred video quality from the dropdown menu.
        4.  **Download:** Click the 'Download Video' button. The video will be saved directly to your computer's 'Downloads' folder.
        
        **Important Notes:**
        *   Only public YouTube videos are supported.
        *   Ensure you have sufficient storage space for the download.
        *   Download speeds may vary based on your internet connection and video size.
        """
    )

st.markdown("<div class='footer'>Made with ❤️ using Streamlit and yt-dlp</div>", unsafe_allow_html=True)
