# -*- coding: utf-8 -*-

from datetime import datetime as dt
from uuid import uuid4
from threading import Timer
import gi
gi.require_version('Notify', '0.7')
from gi.repository import Notify

from fileHandler import writeFile, readFile, str2date
from utilities.lexicalSimilarity import scoreSentence, compareSentence
from utilities.textParser import parseNumber, parseDate
from utilities.GeneralUtilities import error, info

def sort(data):
    """
    Sort list of reminders by time (oldest first).
    """
    return sorted(data, key = lambda k: (k['time']))

def findReminder(string):
    """
    Find reminder by name.

    Search for the given name in the reminderList. A match is determined by similarity
    between request and the available reminder names.
    """
    nameList = [k['name'] for k in reminderList['items']]
    if not len(nameList):
        return (-1, [])
    index, score, indexList = compareSentence(nameList, string)
    if score < 1.0 and not reminderList['items'][index]['hidden']:
        return (index, indexList)
    return (-1, [])

def showAlarm(notification, name):
    info(name)
    notification.show()

def showNotification(name, body):
    """
    Show a notification immediately.
    """
    Notify.Notification.new(name, body).show()

def addReminder(name, time, uuid, body = '', urgency=Notify.Urgency.LOW, hidden = True):
    """
    Queue reminder.

    Show notification at the specified time. With the given name as title and an optional body
    for further information.
    The mandatory is used to identify the reminder and remove it with removeReminder().
    If the reminder should show up in the list printed by 'remind print' hidden (default: True)
    should be set to false. In this case the reminder is requeued at startup. If reminders are
    used e.g. with a todo list for due dates, hidden should probably be set to true so that the
    list is not cluttered with automatically created data.
    If the reminder needs a different priority, it can be set with urgency to critical (=2),
    high (=1) or normal (=0, default).
    """
    waitTime = time - dt.now()
    n = Notify.Notification.new(name, body)
    n.set_urgency(urgency)
    timerList[uuid] = Timer(waitTime.total_seconds(), showAlarm, [n, name])
    timerList[uuid].start()
    newItem = {'name':name, 'time':time, 'hidden':hidden, 'uuid':uuid}
    reminderList['items'].append(newItem)
    reminderList['items'] = sort(reminderList['items'])
    writeFile("reminderlist.txt", reminderList)

def removeReminder(uuid):
    """
    Remove and cancel previously added reminder identified by the given uuid.
    """
    if uuid in timerList:
        timerList[uuid].cancel()
        timerList.pop(uuid)
    for index, e in enumerate(reminderList['items']):
        if uuid == e['uuid']:
            reminderList['items'].remove(reminderList['items'][index])
            break;
    writeFile("reminderlist.txt", reminderList)

actions = {}
def addAction(function, trigger = [], minArgs = 0):
    """
    Add a new action to the list of all available actions.

    :param function: Local function name that should be called when matched
    :param trigger: List of trigger words or sentences
    :param minArgs: Minimum number of arguments needed for given function
    """
    actions[function] = {'trigger': trigger, 'minArgs': minArgs}

addAction("handlerAdd", ["add", "new", "create"], minArgs = 1)
def handlerAdd(data):
    skip, time = parseDate(data)
    if skip:
        addReminder(name=" ".join(data.split()[skip:]), time=time, hidden=False, uuid=uuid4().hex)

addAction("handlerRemove", ["remove", "delete", "destroy"], minArgs = 1)
def handlerRemove(data):
    skip, number = parseNumber(data)
    if skip:
        index = number - 1
    else:
        index, indexList = findReminder(data)
    if index >= 0 and index < len(reminderList['items']):
        info("Removed reminder: \"{0}\"".format(reminderList['items'][index]['name']))
        removeReminder(reminderList['items'][index]['uuid'])
    else:
        error("Could not find selected reminder")

addAction("handlerList", ["list", "print", "show"])
def handlerList(data):
    count = 0
    for index, e in enumerate(reminderList['items']):
        if not e['hidden']:
            print("<{0}> {2}: {1}".format(count + 1, e['time'], e['name']))
            count += 1
    if count == 0:
        info("Reminder list is empty. Add a new entry with 'remind add <time> <name>'")

addAction("handlerClear", ["clear"])
def handlerClear(data):
    reminderList['items'] = [k for k in reminderList['items'] if k['hidden']]
    writeFile("reminderlist.txt", reminderList)

def reminderHandler(data):
    """
    Handle the command string for reminders.
    """
    indices = []
    score = 100
    action = 0
    minArgs = 0
    # Select the best trigger match from the actions list
    for key in actions:
        foundMatch = False
        for trigger in actions[key]['trigger']:
            newScore, indexList = scoreSentence(data, trigger, distancePenalty = 0.5, additionalTargetPenalty = 0, wordMatchPenalty = 0.5)
            if foundMatch and len(indexList) > len(indices):
                # A match for this action was already found.
                # But this trigger matches more words.
                indices = indexList
            if newScore < score:
                if not foundMatch:
                    indices = indexList
                    minArgs = actions[key]['minArgs']
                    foundMatch = True
                score = newScore
                action = key
    if not action:
        return
    data = data.split();
    for i in sorted(indices, reverse=True):
        del data[i]
    if len(data) < minArgs:
        error("Not enough arguments for specified command {0}".format(action))
        return
    data = " ".join(data)
    globals()[action](data)

def reminderQuit():
    """
    This function has to be called when shutting down. It terminates all waiting threads.
    """
    try:
        for index, el in timerList.iteritems():
            el.cancel()
    except:
        for index, el in timerList.items():
            el.cancel()

timerList = {}
reminderList = readFile("reminderlist.txt", {'items':[]})
reminderList['items'] = sort(reminderList['items'])
reminderList['items'] = [i for i in reminderList['items'] if not i['hidden']]
for e in reminderList['items']:
    e['time'] = str2date(e['time'])
    waitTime = e['time'] - dt.now()
    n = Notify.Notification.new(e['name'])
    n.set_urgency(Notify.Urgency.LOW)
    timerList[e['uuid']] = Timer(waitTime.total_seconds(), showAlarm, [n, e['name']])
    timerList[e['uuid']].start()

Notify.init("Jarvis")

