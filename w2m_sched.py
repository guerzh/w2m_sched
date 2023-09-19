# This code scrapes a when2meet URL, parses the availbilities, and then 
# prints out times/days when each subgroup can meet

# The subgroups are specified in the groups dictionary

# This will probably break when when2meet changes its format, if
# it ever worked in the first place. Use at your own risk



import time
# Sample input strings
# time_slots_str = '''TimeOfSlot[0]=1694959200;
# TimeOfSlot[1]=1694960100;
# TimeOfSlot[2]=1694961000;
# TimeOfSlot[3]=1694961900;
# TimeOfSlot[4]=1694962800;'''

# people_str = '''PeopleNames[0] = 'Cameron S';PeopleIDs[0] = 88923263;
# PeopleNames[1] = 'Chunsheng Zuo';PeopleIDs[1] = 88891781;'''

# availability_str = '''AvailableAtSlot[306].push(88890543);
# AvailableAtSlot[305].push(88890543);
# AvailableAtSlot[304].push(88890543);'''


#retrieve html file from https://www.when2meet.com/?21360311-x9kHc
import urllib.request
con = urllib.request.urlopen("https://www.when2meet.com/?21360311-x9kHc")
html = con.read()
con.close()

time_slots_str = "\n".join([x for x in html.decode("utf-8").split("\n") if "TimeOfSlot[" in x and "var " not in x and "document" not in x and "=" in x])
people_str = "\n".join([x for x in html.decode("utf-8").split("\n") if "PeopleNames[" in x and "var " not in x and "document" not in x and "=" in x and "ailableList" not in x])
availability_str = "\n".join([x for x in html.decode("utf-8").split("\n") if "AvailableAtSlot[" in x]) #and "var " not in x and "document" not in x and "=" in x and "if (" not in x and "Math.round" not in x and "ChangeToAvailable" not in x and "SplitSpot" not in x and "new Array" not in x])




# Parsing time slots
time_slots_actual = {}
time_slots_idx = {}
for line in time_slots_str.split(";"):
    if not line.strip():
        continue
    idx, timestamp = map(str.strip, line.split("="))
    time_slots_actual[int(idx.split("[")[1].split("]")[0])] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(timestamp)))
    time_slots_idx[int(idx.split("[")[1].split("]")[0])] =  int(timestamp)


# Parsing people
people = {}
for line in people_str.split(";"):
    if "AvailableAtSlot" in line:
        continue
    
    if "\n<div id=AvailabilityGrids><script type=\"text/javascript\">" in line:
        line  = line.replace("\n<div id=AvailabilityGrids><script type=\"text/javascript\">", "")

    
    if not line.strip():
        continue
    key, value = map(str.strip, line.split("="))
    idx = int(key.split("[")[1].split("]")[0])

    if 'PeopleNames' in key:
        if idx not in people:
            people[idx] = {}
        people[idx]['name'] = value.strip("'")
    elif 'PeopleIDs' in key:
        if idx not in people:
            people[idx] = {}
        people[idx]['id'] = int(value)

# Parsing availabilities
availability = {}
for line in availability_str.split(";"):
    
    if not line.strip():
        continue

    if "AvailableAtSlot" not in line:
        continue
        
    if ".push" not in line:
        continue

    if "-1" in line:
        continue

   #print("line = ", line)
    #idx, person_id = map(str.strip, line[len("AvailableAtSlot["):].split(").push("))
    #idx = int(idx[:-1])
    #person_id = int(person_id[:-1])
    idx = int(line[line.find("[")+1:line.find("]")].strip())
    person_id = int(line[line.find("(")+1:line.find(")")].strip())

    if idx not in availability:
        availability[idx] = []
    availability[idx].append(person_id)

# Store in final dictionary
final_data = {
    "time_slots_actual": time_slots_actual,
    "time_slots_idx": time_slots_idx,
    "people": people,
    "availability": availability
}

print(people)


groups = {"creativity": {"Michael G", "Kamron", "Nikolas Marinkovich"},
          "ML models": {"Michael G", 'Tracy Qian', 'Chunsheng Zuo', 'Amy Saranchuk'},
          "Interpretability": {"Michael G", 'Cameron S', 'Yiping Wang'},
          "ML Social Science": {"Michael G", 'Kailyn (twitter)', 'Juho (Honour Culture)', 'Sophie (challenging test set)'}}


def get_person_id(name, people):
    for person_idx, person in people.items():
        if person['name'] == name:
            return person["id"]
    return None


def get_day_of_week(date):
    return time.strftime("%A", time.strptime(date, "%Y-%m-%d %H:%M:%S"))


for group, names in groups.items():
    for idx in range(len(time_slots_idx)):
        ts_idx = time_slots_idx[idx]
        ts_actual = time_slots_actual[idx]
        day = get_day_of_week(ts_actual)
        if day in ["Saturday", "Sunday"]:
            continue
        
        avail = 0
        for person in names:
            person_id = get_person_id(person, people)
            # print("person_id = ", person_id)
            # print("availability = ", availability[idx])
            if person_id in availability[idx]:
                avail += 1
                
                
        if avail == len(names):
            all_avail = 0
            for i, p in people.items():
                if p["id"] in availability[idx]:
                    all_avail += 1
            
            print("Group", group, "can meet at", ts_actual, "on", day, f"({all_avail})")

                  
                
                    
        

#print(final_data)

# Creativity: Tues 2pm
# Interpretability: Tues 3pm
# ML models: Thurs 4pm
# ML Social Science: Mon 11am
