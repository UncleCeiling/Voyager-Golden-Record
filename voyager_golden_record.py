import requests, os, time
from bs4 import BeautifulSoup

os.chdir(os.path.dirname(__file__))
URL: str = "https://goldenrecord.org/"
FILES_DIR: str = "files/"
IMAGES_DIR: str = "images/"
AUDIO_DIR: str = "audio/"


def get_file(url: str, name: str = "") -> requests.Response | None:
    """Requests a given file from the specified URL if the file does not already exist.

    Args:
        url (str): URL to request the file from
        name (str, optional): Name to save the file as. Defaults to the URL filename if not specified.

    Returns:
        requests.Response | None: Information about the request. None if no request was made.
    """
    if name == "":
        name = FILES_DIR + url.split("/")[-1]
    if os.path.exists(name):
        # print(f"`{name}` file already exists: Skipping...")
        return None
    response = requests.get(url)
    print("Downloaded:", name, " | from: ", url)
    if response.status_code == 200:
        with open(name, "xb") as file:
            file.write(response.content)
    return response


def get_index():
    """Makes sure the `index.html` file exists in `files/`and requests it if it doesn't."""
    if not os.path.exists(FILES_DIR + "index.html"):
        print("`index.html` not found - fetching now.")
        response = get_file(URL + "index.html")
        if response == None:
            return
        elif response.status_code == 200:
            return
        else:
            print(f"Fetch unsuccessful: {response.reason}")
            return
    else:
        print("`index.html` found.")
        return


def save_images(soup: BeautifulSoup):
    """Enumerates then requests the images from the site

    Args:
        soup (BeautifulSoup): `soup` object to enumerate and request.
    """
    if not os.path.exists("images/"):
        os.mkdir("images")
    images = soup.find_all("div", {"class": "carousel-item"})
    skipped = 0
    print(f"Found {len(images)} images. Download starts in 5 seconds.")
    time.sleep(5)
    for image in images:
        file = image.find("img")
        if file == None:
            continue
        url = URL + str(file.get("src"))
        name = (
            IMAGES_DIR
            + url.split("/")[-1].strip(".png")  # Image number
            + " "
            + str(file.get("alt")).replace("/", " of ")
            + ".png"
        )
        response = get_file(url, name)
        if response == None:
            skipped += 1
    if skipped > 0:
        print(f"{skipped} files already exist and were skipped.")


def save_audio(soup: BeautifulSoup):
    """Enumerates then requests the audio files from the site

    Args:
        soup (BeautifulSoup): `soup` object to enumerate and request.
    """
    if not os.path.exists("audio/"):
        os.mkdir("audio")
    audio_src = soup.find_all("source")
    audio_labels = soup.find_all("a", {"class": "list-group-item"})
    skipped = 0
    if len(audio_src) != len(audio_labels):
        print(
            f"""ERROR - Mismatch in number of tracks and number of labels for tracks.
            ({len(audio_src)} to {len(audio_labels)})
            Check `save_audio` function for troubleshooting"""
        )
        exit()
    print(f"Found {len(audio_src)} audio files. Download starts in 5 seconds.")
    time.sleep(5)
    for i in range(len(audio_src)):
        url = URL + str(audio_src[i].get("src"))
        this_audio_label = audio_labels[i].find_all("span")
        track = str(this_audio_label[0].contents[0]).strip(". ")
        name = str(this_audio_label[1].contents[0]).replace("/", "-")
        filename =             AUDIO_DIR + track.rjust(2, "0") + " " + name + ".mp3"
        response = get_file(url, filename)
        if response == None:
            skipped += 1
    if skipped > 0:
        print(f"{skipped} files already exist and were skipped.")


if __name__ == "__main__":
    get_index()
    with open(FILES_DIR + "index.html", "r") as index:
        soup = BeautifulSoup(index, "html.parser")
    save_images(soup)
    save_audio(soup)
