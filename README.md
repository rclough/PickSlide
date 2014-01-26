PickSlide
=========

Started at HAMR 2014 Music Hackathon @ Columbia University.

Have you ever wondered what you would do with a massive data set of 100's of 1000's transcribed and annotated music? What if those transcriptions were rated by users all over the world?

Well, I and a few others were wondering, so I created a hypothetical scraper that will generate a Neo4j database of Guitar Pro files locally donwloaded, linked to metadata around each file.

# What features are captured?

## Tab Files/Nodes

* Relative file location of the guitar pro file
* Rating of the tab
* Number of ratings the tab recieved
* Number of comments on that tab
* Views of that tab
* Properly nested comments, whith ability to track the users commenting in the graph id you wanted
* Title
* Version
* Instruments in the GP file

## User nodes
* Name
* Number of contributions
* Ranking
* Join date
* Can be linked to comments easily (but isn't at the moment)

# What can I use this for?

Guitar pro files have some seriously awesome metadata associated with them:
* Multiple instruments
* Time signatures (good for segmenting)
* Repeat notations (good for segmenting)
* More nuanced notation for instrumetns (bends, slides, vibrato, etc)
* Instrument tuning, incuding capo
* Sometimes musicians are labeled on the individual tracks
* Track Metadata
* Convertable to MIDI
* Occasionally lyrical content

Most of this can already be done with open source code (tux guitar in java, and there exists a really neat ruby library for reading gp3/4/5. This is just a project for hypothetically gathering the data for further feature extraction.

# This code doesnt work/How do I make it work

I don't know! It's purely hypothetical. It supports tab downloads based on a hypothetical security feature involving a salted SHA1, that's about all I can figure out. The code is fairly well commented/named, if you are intelligent, you might be able to make use of it.

##DISCLAIMER:
**I TAKE NO RESPONSIBILITY FOR WHAT YOU DO WITH THIS HYPOTHETICAL CODE EXPERIMENT! IT IS PROVIDED FOR EDUCATIONAL PURPOSES ONLY, WITH ACADEMIC STUDY IN MIND**. I have never run this code on any commercial database.

