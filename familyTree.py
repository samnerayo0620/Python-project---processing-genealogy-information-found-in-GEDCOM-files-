# Samuel Nerayo


"""
GEDCOM parser design

Create empty dictionaries of individuals and families
Ask user for a file name and open the gedcom file
Read a line
Skip lines until a FAM or INDI tag is found
    Call functions to process those two types

Processing an Individual
Get pointer string
Make dictionary entry for pointer with ref to Person object
Find name tag and identify parts (surname, given names, suffix)
Find FAMS and FAMC tags; store FAM references for later linkage
Skip other lines

Processing a family
Get pointer string
Make dictionary entry for pointer with ref to Family object
Find HUSB WIFE and CHIL tags
    Add included pointers to Family object
Skip other lines

Testing to show the data structures:
    Print info from the collections of Person and Family objects
    Print descendant chart after all lines are processed

"""

from collections import namedtuple

# -----------------------------------------------------------------------
# start of class Event
class Event():
#an event class which hold date and place of an event, both can be missing
    def __init__(self):
        self._date = ''
        self._place = ''

    def setDate(self, date):
        self._date = date

    def setPlace(self, place):
        self._place = place

    def eventStr(self):
        return self._date + ' ' + self._place

class Person():
    # Stores info about a single person
    # Created when an Individual (INDI) GEDCOM record is processed.
    # -------------------------------------------------------------------

    def __init__(self, ref):
        # Initializes a new Person object, storing the string (ref) by
        # which it can be referenced.
        self._id = ref
        self._asSpouse = []  # use a list to handle multiple families
        self._asChild = None
        self._birthEvent = None
        self._deathEvent = None
        self._marrEvent = None


    def addName(self, names):
        # Extracts name parts from a list of names and stores them
        self._given = names[0]
        self._surname = names[1]
        self._suffix = names[2]


    def setBirthEvent(self, event):
        # Set the birth event for the person
        self._birthEvent = event

    def setDeathEvent(self, event):
        # Set the death event for the person
        self._deathEvent = event

    def setMarrEvent(self, event):
        # Set the Marriage event for the person
        self._marrEvent = event

    def addIsSpouse(self, famRef):
        # Adds the string (famRef) indicating family in which this person
        # is a spouse, to list of any other such families
        self._asSpouse.append(famRef)

    def addIsChild(self, famRef):
        # Stores the string (famRef) indicating family in which this person
        # is a child
        self._asChild = famRef

    def printDescendants(self, prefix=''):
        # print info for this person and then call method in Family
        print(prefix + self.name() + self.getEvent())

        # recursion stops when self is not a spouse
        for fam in self._asSpouse:
            families[fam].printFamily(self._id, prefix)

    def getDescendants(self):
        # step 2: get the children (which are personID themself)
        # through the family of the person
        descendants = [self._id]
        for fam in self._asSpouse:
            descendants.extend(families[fam].getChildren())
        return descendants

    def printAncestors(self, gen=''):
        # stoping criterial of the recursive function
        # if the person is not child of any family print the
        # generation and the person itself and stop
        if not self._asChild:
            print(gen, len(gen), self.name()+self.getEvent())
        else:
            personFam = families[self._asChild]
            if personFam._spouse1.personRef:
                persons[personFam._spouse1.personRef].printAncestors(gen + ' ')
            if personFam._spouse2.personRef:
                persons[personFam._spouse2.personRef].printAncestors(gen + ' ')
            print(gen, len(gen), self.name() + self.getEvent())

    def getFirstCousins(self):
        # get the first cousins of the person only
        cousins = []
        if self._asChild:
            # get the family of the person
            fam = families[self._asChild]
            if fam._spouse1 and persons[fam._spouse1.personRef]._asChild:
                # get the spouse family
                spouse1Fam = families[persons[fam._spouse1.personRef]._asChild]
                for i in spouse1Fam._children:
                    # loop through that children of the spouse family and grab
                    # the children of the sibilings of the spouse which is not
                    # the parent of the person
                    if i != fam._spouse1.personRef:
                        for j in persons[i]._asSpouse:
                            cousins.extend(families[j]._children)
            # do the same thing for the other spouse
            if fam._spouse2 and persons[fam._spouse2.personRef]._asChild:
                spouse2Fam = families[persons[fam._spouse2.personRef]._asChild]
                for i in spouse2Fam._children:
                    if i != fam._spouse2.personRef:
                        for j in persons[i]._asSpouse:
                            cousins.extend(families[j]._children)
        return cousins

    def getNthCousins(self, n):
        # get the first cousins from the getFirstCousins function
        if n <= 1:
            return self.getFirstCousins()
        else:
            # go to the family of the parent
            nthCousins = []
            if self._asChild:
                fam = families[self._asChild]
                if fam._spouse1.personRef:
                    # get the sibilings of parents
                    nthCousinsParents = persons[fam._spouse1.personRef].getNthCousins(n-1)
                    for i in nthCousinsParents:
                        # loop through the spouses of the sibilings and get their children
                        if persons[i]._asSpouse:
                            for j in persons[i]._asSpouse:
                                nthCousins.extend(families[j]._children)
                # do the same thing for the other parent
                if fam._spouse2:
                    nthCousinsParents = persons[fam._spouse2.personRef].getNthCousins(n-1)
                    for i in nthCousinsParents:
                        if persons[i]._asSpouse:
                            for j in persons[i]._asSpouse:
                                nthCousins.extend(families[j]._children)
            return nthCousins

    def printCousins(self, n=1):
        # by default this function will print the first cousin because n = 1
        cousins = self.getNthCousins(n)
        if str(n).endswith("1"):
            print(str(n) + "st cousins for", self.name())
        elif str(n).endswith("2"):
            print(str(n) + "nd cousins for", self.name())
        elif str(n).endswith("3"):
            print(str(n) + "rd cousins for", self.name())
        else:
            print(str(n) + "th cousins for", self.name())
        if cousins:
            for i in cousins:
                print(persons[i].name() + persons[i].getEvent())
        else:
            print("No cousins")

    def name(self):
        # returns a simple name string
        return self._given + ' ' + self._surname.upper() \
            + ' ' + self._suffix

    def getEvent(self):
        # create a message of the event which are present in this specific person
        message = ""
        if self._marrEvent:
            message += " m " + self._marrEvent.eventStr()
        if self._birthEvent:
            message += " n: " + self._birthEvent.eventStr()
        if self._deathEvent:
            message += " d: " + self._deathEvent.eventStr()
        return message

    def treeInfo(self):
        # returns a string representing the structure references included in self
        if self._asChild:  # make sure value is not None
            childString = ' | asChild: ' + self._asChild
        else:
            childString = ''
        if self._asSpouse != []:  # make sure _asSpouse list is not empty
            # Use join() to put commas between identifiers for multiple families
            # No comma appears if there is only one family on the list
            spouseString = ' | asSpouse: ' + ','.join(self._asSpouse)
        else:
            spouseString = ''
        return childString + spouseString

    def eventInfo(self):
        # add code here to show information from events once they are recognized
        return ''

    def __str__(self):
        # Returns a string representing all info in a Person instance
        # When treeInfo is no longer needed for debugging it can
        return self.name() \
            + self.eventInfo() \
            + self.treeInfo()  ## Comment out when not needed for debugging

    def isDescendant(self,personID):
        #step 1: get the descendant of the person itself
        if personID == self._id:
            return True
        if personID in self.getDescendants():
            return True
        else:
            return False

# end of class Person
# -----------------------------------------------------------------------


# Declare a named tuple type used by Family to create a list of spouses
Spouse = namedtuple('Spouse', ['personRef', 'tag'])


class Family():
    # Stores info about a family
    # An instance is created when an Family (FAM) GEDCOM record is processed.
    # -------------------------------------------------------------------

    def __init__(self, ref):
        # Initializes a new Family object, storing the string (ref) by
        # which it can be referenced.
        self._id = ref
        self._spouse1 = None
        self._spouse2 = None
        self._children = []

    def addSpouse(self, personRef, tag):
        # Stores the string (personRef) indicating a spouse in this family
        newSpouse = Spouse(personRef, tag)
        if self._spouse1 == None:
            self._spouse1 = newSpouse
        else:
            self._spouse2 = newSpouse

    def addChild(self, personRef):
        # Adds the string (personRef) indicating a new child to the list
        self._children.append(personRef)

    def printFamily(self, firstSpouse, prefix):
        # Used by printDecendants in Person to print other spouse
        # and recursively invoke printDescendants on children

        # Manipulate prefix to prepare for adding a spouse and children
        if prefix != '': prefix = prefix[:-2] + '  '

        # Print out a '+' and the name of the second spouse, if present
        if self._spouse2:  # check for the presence of a second spouse
            # If a second spouse is included, figure out which is the
            # "other" spouse relative to the descendant firstSpouse
            if self._spouse1.personRef == firstSpouse:
                secondSpouse = self._spouse2.personRef
            else:
                secondSpouse = self._spouse1.personRef
            print(prefix + '+' + persons[secondSpouse].name())

        # Make a recursive call for each child in this family
        for child in self._children:
            persons[child].printDescendants(prefix + '|--')

    def getChildren(self):
        # step 3: return all the children and their descendants.
        children = [self._children]
        for child in self._children:
            children.extend(persons[child].getDescendants())
        return children

    def __str__(self):
        ## Constructs a single string including all info about this Family instance
        spousePart = ''
        for spouse in (self._spouse1, self._spouse2):  # spouse will be a Spouse namedtuple (spouseRef,tag)
            if spouse:  # check that spouse is not None
                if spouse.tag == 'HUSB':
                    spousePart += ' Husband: ' + spouse.personRef
                else:
                    spousePart += ' Wife: ' + spouse.personRef
        childrenPart = '' if self._children == [] \
            else ' Children: ' + ','.join(self._children)
        return spousePart + childrenPart

# end of class Family
# -----------------------------------------------------------------------


# Global dictionaries used by Person and Family to map INDI and FAM identifier
# strings to corresponding object instances

persons = dict()  # saves references to all of the Person objects
families = dict()  # saves references to all of the Family objects


## Access functions to map identifier strings to Person and Family objects
## Meant to be used in a module that tests this one

def getPerson(personID):
    return persons[personID]


def getFamily(familyID):
    return families[familyID]


## Print functions that print the info in all Person and Family objects
## Meant to be used in a module that tests this one
def printAllPersonInfo():
    # Print out all information stored about individuals
    for ref in sorted(persons.keys()):
        print(ref + ':' + str(persons[ref]))
    print()


def printAllFamilyInfo():
    # Print out all information stored about families
    for ref in sorted(families.keys()):
        print(ref + ':' + str(families[ref]))
    print()


# -----------------------------------------------------------------------

def processGEDCOM(file):
    def getPointer(line):
        # A helper function used in multiple places in the next two functions
        # Depends on the syntax of pointers in certain GEDCOM elements
        # Returns the string of the pointer without surrounding '@'s or trailing
        return line[8:].split('@')[0]

    def processPerson(newPerson):
        nonlocal line
        line = f.readline()
        while line[0] != '0':  # process all lines until next 0-level
            found = False
            tag = line[2:6]  # substring where tags are found in 0-level elements
            if tag == 'NAME':
                names = line[6:].split('/')  # surname is surrounded by slashes
                names[0] = names[0].strip()
                names[2] = names[2].strip()
                newPerson.addName(names)
            elif tag == 'FAMS':
                newPerson.addIsSpouse(getPointer(line))
            elif tag == 'FAMC':
                newPerson.addIsChild(getPointer(line))
            ## add code here to look for other fields
            if tag == "BIRT":
                birthEvent = Event()
                line = f.readline()
                while line.startswith('2'):
                    Line = line.strip().split()
                    if line.startswith('2 DATE'):
                        dateLine = ' '.join(Line[2:])
                        birthEvent.setDate(dateLine.strip())
                    elif line.startswith('2 PLAC'):
                        placeLine = line[7: ]
                        birthEvent.setPlace(placeLine.strip())
                    line = f.readline()
                    found = True
                 # Set the birth event for the person
                newPerson.setBirthEvent(birthEvent)
            elif tag == "DEAT":
                deathEvent = Event()
                line = f.readline()
                while line.startswith('2'):
                    Line = line.strip().split()
                    if line.startswith('2 DATE'):
                        dateLine = ' '.join(Line[2:])
                        deathEvent.setDate(dateLine.strip())
                    elif line.startswith('2 PLAC'):
                        placeLine = line[7: ]
                        deathEvent.setPlace(placeLine.strip())
                    line = f.readline()
                    found = True
                 # Set the death event for the person
                newPerson.setDeathEvent(deathEvent)
            elif tag == "MARR":
                marrEvent = Event()
                line = f.readline()
                while line.startswith('2'):
                    Line = line.strip().split()
                    if line.startswith('2 DATE'):
                        dateLine = ' '.join(Line[2:])
                        marrEvent.setDate(dateLine.strip())
                    elif line.startswith('2 PLAC'):
                        placeLine = line[7: ]
                        marrEvent.setPlace(placeLine.strip())
                    line = f.readline()
                    found = True
                 # Set the marriage event for the person
                newPerson.setMarrEvent(marrEvent)

            if not found:
                # read to go to next line
                line = f.readline()

    def processFamily(newFamily):
        nonlocal line
        line = f.readline()
        while line[0] != '0':  # process all lines until next 0-level
            tag = line[2:6]
            if tag == 'HUSB':
                newFamily.addSpouse(getPointer(line), 'HUSB')
            elif tag == 'WIFE':
                newFamily.addSpouse(getPointer(line), 'WIFE')
            elif tag == 'CHIL':
                newFamily.addChild(getPointer(line))
            # read to go to next line
            line = f.readline()

    ## f is the file handle for the GEDCOM file, visible to helper functions
    ## line is the "current line" which may be changed by helper functions

    f = open(file)
    line = f.readline()
    while line != '':  # end loop when file is empty
        fields = line.strip().split(' ')
        if line[0] == '0' and len(fields) > 2:
            if (fields[2] == "INDI"):
                ref = fields[1].strip('@')
                ## create a new Person and save it in mapping dictionary
                persons[ref] = Person(ref)
                ## process remainder of the INDI record
                processPerson(persons[ref])

            elif (fields[2] == "FAM"):
                ref = fields[1].strip('@')
                ## create a new Family and save it in mapping dictionary
                families[ref] = Family(ref)
                ## process remainder of the FAM record
                processFamily(families[ref])

            else:  # 0-level line, but not of interest -- skip it
                line = f.readline()
        else:  # skip lines until next candidate 0-level line
            line = f.readline()

    ## End of ProcessGEDCOM


# -----------------------------------------------------------------------
## Test code starts here

def print_header(header):
    print(f"\n{'=' * 30}")
    print(f"{header}")
    print(f"{'=' * 30}")

def main():
    filename = "Kennedy.ged"  # Set a default name for the file to be processed
    # Uncomment the next line to make the program interactive
    filename = input("Type the name of the GEDCOM file:")

    processGEDCOM(filename)

    print_header("Printing all Persons info:")
    printAllPersonInfo()

    print_header("Printing all Families info:")
    printAllFamilyInfo()

    person = "I46"  # Default selection to work with Kennedy.ged file
    # Uncomment the next line to make the program interactive
    person = input("Enter person ID for descendants chart:")

    print("Printing the Descendants of:", getPerson(person).name())
    getPerson(person).printDescendants()

if __name__ == '__main__':
    main()

