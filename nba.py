import requests
import re
from turtle import *
import xlwt

def getHTMLText(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ""

def getTeamNames():
    text = getHTMLText("https://www.basketball-reference.com/")
    teams = re.findall(r"value=\"[A-Z]{3}\".*?<", text)
    for i in range(len(teams)):
        words = teams[i].split(" ")
        teams[i] = words[len(words) - 1][0:-1].lower()
    return teams

def getScoresDiff(teams):
    ret = {}
    for team in teams:
        ret[team] = getTeamScroesDiff(team)
    return ret

def getTeamScroesDiff(team): #for test
    link = "https://nba.hupu.com/schedule/" + team
    html = getHTMLText(link)
    diff = []
    rawScores = re.findall(r"\d{2,3}&nbsp;-&nbsp;\d{2,3}", html)
    rawTeams = re.findall(r";<a href=\"https://nba.hupu.com/teams/.*?\"", html)
    for i in range(len(rawScores)):  # 季前赛待处理
        scores = rawScores[i].split("&nbsp;-&nbsp;")
        dif = int(scores[0]) - int(scores[1])
        if rawTeams[i].endswith(team + "\""):
            dif = - dif
        diff.append(dif)
    print("finish " + team)
    print(diff)
    return diff[-82:]

def toExcel(path, teams, allDiffs):
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet("sheet1")
    for i in range(len(teams)):
        sheet.write(i, 0, teams[i])
        diffs = allDiffs[teams[i]]
        for j in range(len(diffs)):
            sheet.write(i, j + 1, diffs[j])
    workbook.save(path)

def x(x):
    return x - width / 2

def y(y):
    return y - height / 2

def line(x, y, width, height):
    penup()
    goto(x, y)
    pendown()
    goto(x + width, y + height)

def drawRect(x, y, width, height, bondcolor = "black"):
    penup()
    goto(x, y)
    pendown()
    color(bondcolor)
    goto(x, y + height)
    goto(x + width, y + height)
    goto(x + width, y)
    goto(x, y)

def fillRect(x, y, width, height):
    penup()
    goto(x, y)
    pendown()
    begin_fill()
    fillColor = "red"
    if height < 0:
        fillColor = "green"
    color(fillColor)
    goto(x, y + height)
    goto(x + width, y + height)
    goto(x + width, y)
    goto(x, y)
    end_fill()
    color("black")

def rect(x, y, width, height):
    fillRect(x, y, width, height)
    drawRect(x, y, width, height)

def writeText(x, y, text, title = False):
    penup()
    goto(x, y)
    pendown()
    if title:
        write(text, align = "center",  font=("Arial", 12, "bold"))
    else:
        write(text, align="center")

def getBound(bound, num = 20):
    return (int (bound / num) + 1) * num

def draw(team, diffs):
    hideturtle()
    speed(10)
    width = 1100
    height = 600
    extra = 20
    left = - width / 2 + extra
    right = width / 2 + extra
    top = height / 2
    bottom = - height / 2

    high = 0
    low = 0
    sum = 0
    for diff in diffs:
        sum += diff
        low = min(sum, low)
        high = max(sum, high)

    upperBound = getBound(high)
    print ("upperbound = " + str(upperBound))
    lowerBound = - getBound(- low)
    print("lowerbound = " + str(lowerBound))
    unitY = height / (upperBound - lowerBound)
    gap = 20

    writeText(left - 50 - extra, 0, team, True)

    line(left, bottom, 0, height)
    startY = bottom - lowerBound * unitY
    line(left, startY, width + 50 , 0)
    games = 82
    unitX = width / games
    for i in range(1, games + 1):
        xi = x(unitX * i) + extra
        line(xi, startY, 0, 10)
        writeText(xi, startY - 15, str(i))

    for i in range(lowerBound, upperBound + gap, gap):
        y = i * unitY
        line(left, i * unitY + startY, width + 50, 0)
        writeText(left - 15, y + startY, str(i))
        i += gap
    sum = 0
    wFactor = 0.7
    pensize(1)
    for i in range(len(diffs)):
        rect(x((i + 1 - wFactor / 2) * unitX) + extra, startY + sum * unitY, unitX * wFactor, diffs[i] * unitY)
        sum += diffs[i]
    ts = getscreen()
    ts.getcanvas().postscript(file=team + ".eps")
    clear()

global width
width = 1100
global height
height = 600
teams = getTeamNames()
allDiffs = getScoresDiff(teams)
print(allDiffs)
toExcel("C:/Users/willi/Desktop/NBA.xls", teams, allDiffs)
for team in teams:
    draw(team, allDiffs)
