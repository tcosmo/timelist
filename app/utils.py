import os, uuid

def reformate_markdown(raw_content):
    """ Converts `SimpleMDE` Markdown to python markdown.markdown.
    """
    to_return = ""
    print(raw_content)
    for ligne in raw_content.split("\r\n"):
        print("#", ligne.strip())
        #if len(ligne.strip()) == 0:

        if len(ligne) != 0 and '#' in ligne and ligne.strip()[0] == '#':
            to_return += ligne + "\n"
        else:
            to_return += ligne + "   " +"\n"


    to_return = to_return.replace('*','-')

    return to_return

def timeMarkToStr( tm ):
    """ Transforms int 9 to 09 for pretty date printing.
    """
    if len(str(tm)) == 1:
        return "0"+str(tm)
    return str(tm)

def createNewEntryFolder():
    filename = str(uuid.uuid4())

    while os.path.exists('app/static/entries/'+filename):
        filename = str(uuid.uuid4().hex)

    os.makedirs('app/static/entries/'+filename)

    return filename