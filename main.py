import random
from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageClip, CompositeVideoClip, AudioFileClip, CompositeAudioClip
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import os
import glob
import pyttsx3
import audioread
import random
import math
import pathlib
from datetime import date
import sys

os.environ['MOZ_HEADLESS'] = '1'

# List of inappropriate words to censor for TikTok
blacklist = {
    "fuck": "freak",
    "shit": "shoot",
    "dick": "pp",
    "penis": "pp",
    "asshole": "bad guy",
    "bitch": "big",
    "cunt": "cat",
    "slut": "shut",
    "whore": "whole",
    "nigga": "friend",
    "kill": "cool",
    "masturbate": "do good",
    "masturbating": "doing good",
    "sex": "funtime",
    "drug": "candy"
    }

def main():
    global titles, comments, length, number_of_comments, number_of_posts, date_today, time_now
    titles = []
    comments = []
    length = []
    number_of_comments = 7

    if len(sys.argv) == 1:
        link = ""
        number_of_posts = int(input("Number of posts: "))
    elif len(sys.argv) == 2:
        link = sys.argv[1]
        number_of_posts = 1
    else:
        print("Invalid number of arguments.")
        quit()

    date_today = date.today().strftime("%d%B")
    time_now = f"{time.localtime().tm_hour:02}{time.localtime().tm_min:02}"
    for _ in range(number_of_posts):
        length.append(0)

    # Creating a data folder for all the screenshots and mp3's
    data_folder_path = str(pathlib.Path(__file__).parent.absolute()) + "\data"
    if not os.path.isdir(data_folder_path):
        os.mkdir("data")

    downloading_content(link)
    creatingmp3s()
    videoediting()
    deletingfiles()

# Censoring the text
def censor(text):
    global blacklist
    for key in blacklist:
        if text.lower().find(key) != -1:
            text = text.replace(key, blacklist.get(key))
    return text

def downloading_content(link):
    global number_of_comments, number_of_posts, titles, comments

    # Getting login info
    login_info = []
    with open("login_info.txt", "r") as f:
        lines = f.readlines()
    for line in lines:
        login_info.append(line)
    login = login_info[0]
    password = login_info[1]

    # Openning browser
    browser = webdriver.Firefox()
    browser.set_window_size(450, 1000)
    link_login = "https://www.reddit.com/login/?dest=https%3A%2F%2Fwww.reddit.com%2Fr%2FAskReddit%2Ftop%2F%3Ft%3Dday"
    browser.get(link_login)
    print("Reddit opened")

    # Logging in
    input_username = browser.find_element("id", "loginUsername")
    input_password = browser.find_element("id", "loginPassword")
    input_username.send_keys(login)
    input_password.send_keys(password)
    input_password.send_keys(Keys.ENTER)
    print(f"Logged in as {login}")
    time.sleep(8)

    # Finding the best posts if the link wasn't specified
    if len(link) == 0:
        all_posts = browser.find_elements(By.CLASS_NAME, "SQnoC3ObvgnGjWt90zD9Z._2INHSNB8V5eaWp4P0rY_mE")
        all_posts = all_posts[:number_of_posts]
        links = []
        for post in all_posts:
            links.append(post.get_attribute('href'))
        print(f"Saved {len(links)} of the best posts!")
    else:
        links = [link]
        print("Saved the post!")

    # Rejecting cookies
    section = browser.find_element(By.CSS_SELECTOR, "button._1tI68pPnLBjR1iHcL7vsee")
    section.click()

    # Forcing Reddit to show a pop-up window
    browser.get("https://www.reddit.com/r/AskReddit/comments/vxak2u/what_is_the_biggest_lie_sold_to_your_generation/")
    time.sleep(3)

    # Iterating through all the links
    counter = 1
    for link in links:
        browser.get(f"{link}?sort=top")
        time.sleep(3)

        # Getting the title and screenshotting it
        while True:
            try:
                title = browser.find_element(By.CLASS_NAME, "_eYtD2XCVieq6emjKBH3m").text
            except:
                print("Couldn't find the title. Trying again in 5 sec...")
                time.sleep(5)
            else:
                break
        title = censor(title)
        titles.append(title.capitalize())
        print(f"Post #{counter}: {title}")
        while True:
            try:
                title_ss = browser.find_element(By.XPATH, "//div[@data-testid='post-container']")
            except:
                print("Couldn't screenshot the title. Trying again in 5 sec...")
                time.sleep(5)
            else:
                break
        title_ss.screenshot(f"data\\title{counter}.png")
        print("Title saved")

        # Getting comments and screenshotting them
        comms_found = []
        Y = 1080
        while len(comms_found) < number_of_comments:
            browser.execute_script(f"window.scrollTo(0, {Y})")
            comms_found = browser.find_elements(By.CSS_SELECTOR, "div.Comment._1z5rdmX8TDr6mqwNv7A70U")
            Y += 1080
        comms_found = comms_found[:number_of_comments]
        comments_counter = 0
        time.sleep(3)
        for comm in comms_found:
            comments_counter += 1
            comm.screenshot(f"data\\comment{counter}v{comments_counter}.png")
            texts = comm.find_elements(By.XPATH, ".//p")
            comment = []
            for text in texts:
                tekst = censor(text.text)
                comment.append(tekst)
            comments.append('. '.join(comment))
        print(f"Saved {comments_counter} comments")
        counter += 1
    browser.quit()

# Creating MP3 files
def creatingmp3s():
    global titles, comments, length, number_of_comments
    print("Creating MP3 files...")
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 200)
    for i in range(len(titles)):
        engine.save_to_file(titles[i], f'data\\title{i+1}.mp3')
        engine.runAndWait()
        with audioread.audio_open(f'data\\title{i+1}.mp3') as f:
            length[i] += f.duration
        for k in range(number_of_comments):
            engine.save_to_file(comments[k], f'data\\comment{i+1}v{k+1}.mp3')
            engine.runAndWait()
            with audioread.audio_open(f'data\\comment{i+1}v{k+1}.mp3') as f:
                length[i] += f.duration
        if len(comments) > 0:
            comments = comments[number_of_comments:]
    print("Created MP3 files!")

# Putting the video together
def videoediting():
    global time_now, length, date_today
    for i in range(number_of_posts):
        print(f"\nVideo #{i+1}")
        whole_length = 0

        # Starting to edit
        print("Video editing...")
        maxstart = 530 - math.ceil(length[i])
        if maxstart < 0: maxstart = 0
        minutes = math.ceil(length[i]) // 60
        seconds = math.ceil(length[i]) % 60
        #print (f"Video length: {minutes}m{seconds}s")
        time_pointer = random.randrange(maxstart)
        background = VideoFileClip("files\\mcbg.mp4").without_audio().crop(x_center=960, y_center=540, width=576, height=1024)
        voice = AudioFileClip(f"data\\title{i+1}.mp3")
        title_im = ImageClip(f"data\\title{i+1}.png")
        with audioread.audio_open(f"data\\title{i+1}.mp3") as f:
            duration = f.duration
            whole_length += duration
        background_cut = background.subclip(time_pointer,time_pointer+duration)
        final = CompositeVideoClip([background_cut, title_im.resize(width=450).set_position(("center","center")).set_start(0).set_duration(duration)]).set_audio(voice)
        time_pointer += duration

        # Creating a clip for every comment (background video + comment screenshot + audio)
        for k in range(number_of_comments):
            if whole_length > 120:
                print("Length of the video reached over 2 min.")
                break
            comment_image = ImageClip(f"data\\comment{i+1}v{k+1}.png")
            voice = AudioFileClip(f"data\\comment{i+1}v{k+1}.mp3")
            print(f"Comment {k+1}")
            with audioread.audio_open(f"data\\comment{i+1}v{k+1}.mp3") as f:
                duration = f.duration
                whole_length += duration
                f.close()
            background_cut = background.subclip(time_pointer, time_pointer+duration)
            one_comment_video = CompositeVideoClip([background_cut, comment_image.resize(width=450).set_position(("center","center")).set_start(0).set_duration(duration)]).set_audio(voice)
            
            # Adding the clip to the final video
            final = concatenate_videoclips([final, one_comment_video])
            time_pointer += duration

        # Adding background music
        background_music = AudioFileClip("files\\musicbg.mp3")
        only_video_audio = final.audio
        duration = only_video_audio.duration
        final_audio = CompositeAudioClip([only_video_audio, background_music.volumex(0.08).subclip(0, duration)])
        final.audio = final_audio
        ms = math.ceil(duration) // 60
        ss = math.ceil(duration) % 60
        print (f"Video length: {ms}m{ss}s")

        # Saving the video
        video_name = f"Reddit-{date_today}-{time_now}_({i+1}).mp4"
        try:
            final.write_videofile(video_name)
        except Exception:
            print(f"Couldn't save the video: {Exception}")
        else:
            print(f"Saved {video_name}")  

        background.reader.close()
        background_cut.reader.close()

# Deleting files
def deletingfiles():
    time.sleep(1)
    files = glob.glob(str(pathlib.Path(__file__).parent.absolute()) + "\data\*")
    for f in files:
        try:
            os.remove(f)
        except Exception:
            print(f"Couldn't remove file {str(f)}: {Exception}")
    try:
        os.rmdir("data")
    except Exception:
        print(f"Couldn't remove the data folder: {Exception}")
    else:
        print("Files deleted")

if __name__ == "__main__":
    main()
