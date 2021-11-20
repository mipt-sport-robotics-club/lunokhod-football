import json

with open('data/language.json', 'r+', encoding='utf-8') as f:
    language = json.load(f)

with open('data/camsConfig.json', 'r+', encoding='utf-8') as f:
    camConfig = json.load(f)

with open('data/keyboard.json', 'r+', encoding='utf-8') as f:
    keyboard = json.load(f)

with open('data/settings.json', 'r+', encoding='utf-8') as f:
    settings = json.load(f)

topicRoot = "MIPT-SportRoboticsClub/LunokhodFootball/RawARUCO/#"
topicBall = "MIPT-SportRoboticsClub/LunokhodFootball/RawBALL/#"
topicRobot = "MIPT-SportRoboticsClub/LunokhodFootball/Robots/"

pitchCornerIdList = [1, 2, 3]
robotIdList = [4, 5, 6, 7, 8, 9, 10, 11]
pitchSize = (474, 336)
cameraResolution = (640, 480)
width, height = 1280, 720

zm_pattern = "http://{0}/zm/cgi-bin/nph-zms?scale=100&width=640px&height=480px&mode=jpeg&maxfps=30&monitor={1}&connkey={2}&user={3}&pass={4}"
