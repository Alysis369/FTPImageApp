# FTP_image_app

An demo version application to pull images from an FTP server implementation.
Repo is geared towards development used. Prod use will be compiled through PyInstaller.

------

# Quickstart

#### Start DB Container

```commandline
cd DB
docker compose up -d
```

#### Start App

```python
python
ftp_app_main.py
```

--------------

# Description

Goal of the FTP_image_app is to create an executable app.\
\
Based on user input, the app will transact with 2 local databases to create a list of images to download from an
FTP server, saving images to a user-specified directory.

![Overall Demo](https://github.com/Alysis369/FTPImageApp/blob/dev/Misc/draft_demo.gif)

### Design

###### Data Flow Diagram

![DataFlowDiagram](https://github.com/Alysis369/FTPImageApp/blob/dev/Misc/Ftp_image_app_Data_Flow_Diagram.png)

###### Class UML Diagram

![ClassDiagram](https://github.com/Alysis369/FTPImageApp/blob/dev/Misc/Ftp_image_app_UML_Diagram.png)

### Prerequisite
- Docker 
- Prerequisite python libraries

###### Prerequisite Python Libraries

Prerequisite libraries contained in *requirements.txt.* 

```commandline
pip install -r requirements.txt
```

------

# Demo Environment

### Description

Demo test environment includes:

- PTDB (*Local MySQL DB*): Contains part data information, including reject criteria
- ImgDB (*Local MySQL DB*): Contains FTP imagepath information
- ImgFTP (*Local VSMTP*): Contains images

Whole environment is docker-specified and spawned.

### DB ERD

###### PTDB ERD

*user: root | password: password*\
![PTDB_ERD](https://github.com/Alysis369/FTPImageApp/blob/dev/Misc/ptdb_eng_erd.png)

###### IMGDB ERD

*user: root | password: password*\
![IMGDB_ERD](https://github.com/Alysis369/FTPImageApp/blob/dev/Misc/imgdb_eng_erd.png)

### FTP Image Server

Image server contains 24 sample images of different iconic characters from Nintendo and SquareEnix games.

*user: user | password: pass*

Characters are referred differently in the app:

- Line: Game company (Nintendo/SquareEnix)
- Eq: Character (Ex. Mario, Luigi)
- Eq_num: Character Descriptions
- Reject: Specific attribute of Character

Characters (*referred in the app as Equipment*) includes:

- Nintendo: Mario, Luigi and Peach
- SquareEnix: Sora, Cloud, Tifa

### Demo Environment Limitation

- With the current data present in the DB, parts were created on *2024-03-11 01:05:54*.
  **Start_date and End_date must encompass this datetime.**

------

# Miscellaneous

### Progress

- 2/29: Created producer and GUI threading
- 3/6: Created worker threading
- 3/8: Created MySQL container and tables
- 3/10: Established test db/ftp server, connected eq selection to DB
- 3/11: Finished first draft of fully working App
- 3/15: Handled DB/FTP connection timeout on startup, DB/FTP connection during pull
- 3/15: Added threading to DB calls, increase speed in prod
- 3/15: Added home_dir validation

-----

### TODO/Future Features

##### Known Bugs
- Connection to DB stalls on launched, but paused DB container

##### Learning Lessons
- Create custom DB thread per thread, easier to handle

##### Dev Changes

- ~~Use threading to execute db calls to both db, prod might be slow and IO bound~~ *Updated 3/15*
- ImgPath list and txid list comparison is O(N*M)
    - possible for chunking and multiprocessing?
    - after every cross check, add job to queue instead of processing whole list, figure out how to determine job size
- Add feature for ALL images, and add support for VV images
- FTP requires spawning a different connection for each img download.. 
- ~~Check connection upon application startup, displays warning and exits gracefully.~~ *Updated 3/15*
- ~~Add homepath validation~~ Added 3/15
- Add error status to GUI

##### Prod Changes
- Add reject_code support to GUI 
  - Combine df from DB call, unparse them upon selection
- Prod to inherit ftp_app_model class to adjust to prod environment
- Prod to support multi-date pull, and organize the folder automatically per date


