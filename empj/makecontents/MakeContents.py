#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
try:
    from lxml import etree, html
except ImportError:
    import xml.etree.ElementTree as etree, html
import json
import os
#from evernote.api.client import EvernoteClient
import evernote.edam.notestore.ttypes as NSTypes
# import evernote.edam.notestore as NoteStore
import evernote.edam.type.ttypes as Types
import evernote.edam.error.ttypes as Errors 
from evernote.edam.error.ttypes import EDAMErrorCode
from evernote.edam.error.ttypes import EDAMNotFoundException

# Global Constants
MIN = 60
sleep_time_min = 30 * MIN
note_data = {}
here = os.path.dirname(__file__)


def to_unicode(unicode_or_str):
    ''' Always return unicode'''
    if isinstance(unicode_or_str, str):
        value = unicode_or_str.decode('utf-8')
    else:
        value = unicode_or_str
    return value  # unicodeのインスタンス


def to_str(unicode_or_str):
    '''Always return str'''
    if isinstance(unicode_or_str, unicode):
        value = unicode_or_str.encode('utf-8')
    else:
        value = unicode_or_str
    return value  # strのインスタンス


def makeValueList(data, tag, key):
    '''
    Make a value list from data
    '''
    return [d[key] for d in data[tag]]
    

def setNotebooksGuidJson(note_store):
    '''
    Set notebook GUIDs in data file
    '''
    notebooks = note_store.listNotebooks()
    notebook_names = [nb.name for nb in notebooks]
    for notebook in note_data['notebooks']:
        if notebook['name'] in notebook_names:
            i = notebook_names.index(notebook['name'])
            notebook['guid'] = notebooks[i].guid
        else:
            raise Exception('Found no notebook: {}'.format(notebook['name']))


def setTagGuidJson(note_store):
    '''
    Set tag GUIDs in data file
    '''
    tags = note_store.listTags()
    tag_names = [t.name for t in tags]
    for tag in note_data['tags']:
        if tag['name'] in tag_names:
            i = tag_names.index(tag['name'])
            tag['guid'] = tags[i].guid
        else:
            raise Exception('Found no tag: {}'.format(tag['name']))


def checkDataFile(note_store):
    '''
    Check data file and store app data from Evernote
    '''
    # Check notebook data (name, guid)
    for notebook in note_data['notebooks']:
        if not notebook['name']:
            raise Exception('Error: note data is collapsed.\nnotebook name is not specified')
        setNotebooksGuidJson(note_store)

    # Check tag data (guid)
    for tag in note_data['tags']:
        if not tag['name']:
            raise Exception('Error: note data is collapsed.\ntag name is not specified')
        setTagGuidJson(note_store)


def updateNoteData(meta_note):
    '''
    Update stored note data
    '''
    guids = makeValueList(note_data, 'notes', 'guid')
    i = guids.index(meta_note.guid)
    if meta_note.updateSequenceNum > note_data['notes'][i]['updateSequenceNum']:
        note_data['notes'][i]['title'] = meta_note.title
        note_data['notes'][i]['updateSequenceNum'] = meta_note.updateSequenceNum
        note_data['notes'][i]['updated'] = True
        note_data['notes'][i]['notebook']['guid'] = meta_note.notebookGuid
    else:
        pass


def createNoteData(meta_note):
    '''
    Create new note data
    '''
    note_data['notes'].append(
        {
            "notebook": {
                "name": "",
                "guid": meta_note.notebookGuid
            },
            "title": meta_note.title,
            "guid": meta_note.guid,
            "updateSequenceNum": meta_note.updateSequenceNum,
            "updated": True,
        },
    )


def storeMetadata(note_store):
    '''
    Store tagged metadata in data file
    '''
    filter = NSTypes.NoteFilter()
    resultSpec = NSTypes.NotesMetadataResultSpec()
    for notebook in note_data['notebooks']:
        filter.notebookGuid = notebook['guid']
        filter.tagGuids = makeValueList(note_data, 'tags', 'guid')
        resultSpec.includeTitle = True
        resultSpec.includeUpdateSequenceNum = True
        resultSpec.includeNotebookGuid = True
        try:
            metalist = note_store.findNotesMetadata(filter, 0, 250, resultSpec)
            meta_notes = metalist.notes
            if not meta_notes:
                raise Exception('Found no tagged note')
        except EDAMNotFoundException as e:
            raise Exception('Found wrong {}'.format(e.identifier))
        except Exception as e:
            raise Exception(e)
        #
        guids = makeValueList(note_data, 'notes', 'guid')
        meta_notes_create = []
        # Update
        for mn in meta_notes:
            if mn.guid in guids:
                updateNoteData(mn)
            else:
                meta_notes_create.append(mn)
        # Create
        for mn in meta_notes_create:
            createNoteData(mn)


def checkNotebooksUpdate(note_store):
    '''
    Check notebooks update
    '''
    # Get Evernote State
    current_state = note_store.getSyncState()
    print current_state                                  # debug
    last_update_count = note_data.get('updateCount', 0)

    # Check update count
    current_update_count = current_state.updateCount
    if current_update_count > last_update_count:
        res = True
        print 'Yes, something is updated!'              # debug
    else:
        res = False
        print 'No, nothing is updated.'                 # debug

    return res


def eNoteUpdate(note_store):
    '''
    Update Evernote
    '''
    def isrighttag(x):
        for an in x.iterancestors():
            if an.tag == 'en-note':
                return True
            elif an.tag != 'div':
                return False
        

    for note in note_data['notes']:
        if not note['updated']:
            continue
        #
        print u'updating \'{}\''.format(to_unicode(note['title'])) + u'....'
        content = note_store.getNoteContent(note['guid'])
        #tree = etree.fromstring(content)
        tree = html.fromstring(content)
        # Remove old contents section
        try:
            if 'CONTENTS' in tree[0].itertext():
                tree.remove(tree[0])
                for child in tree.getchildren():
                    if 'hr' in [ch.tag for ch in child.iterchildren()]:
                        tree.remove(child)
                        break
                    else:
                        tree.remove(child)
        except Exception as e:
            raise Exception('Ended at contents removal :{}'.format(e))

        # Make contents section
        contents_list = []
        # Search all xpath for bold text
        xp = tree.xpath(
            '//span[1][@style="font-weight: bold;"] |\
            //strong[1] | //b[1]') 
        # xp = tree.xpath(
        #     '//en-note/div/div/span[@style="font-weight: bold;"] |\
        #     //en-note/div/div/div/span[@style="font-weight: bold;"] |\
        #     //en-note/div/div/strong | //en-note/div/div/b') 
        # Get bold text
        for x in xp:
            text = x.text
            if not text:
                continue
            ix = list(x.getparent().itertext()).index(text)
            if ix == 0 and isrighttag(x):        
                con = etree.tostring(x)
                for sib in x.itersiblings():
                    con += etree.tostring(sib)
                contents_list.append(con)

        # for x in xp:
        #     text = list(x.itertext())
        #     if list(x.getparent().itertext()).index(text[0]) == 0:
        #         contents_list.append(etree.tostring(x))

        # for x in xp:
        #     n = len(list(x.getparent().itertext()))
        #     if  n == 1 or n == 2:
        #         contents_list.append(etree.tostring(x))  # get a raw text
        
        # for content in tree.xpath('/en-note/div/div/span | /en-note/div/strong'):
        #     texts = list(div.itertext())
        #     tags = [d.tag for d in div.iterdescendants()]      # get all children recursively
        #     if len(texts) == 1 and 'strong' in tags:
        #         contents_list.append(texts[0])

        div_contents = '<div><span style="font-size: 18px;"><strong>CONTENTS</strong></span></div>'
        for text in contents_list:
            div_contents += '<div>' + text + '</div>'
        div_contents += '<div><hr/></div>'

        # Make note content
        body = ''
        for e in tree:
            body += etree.tostring(e) 
        new_content = '<?xml version="1.0" encoding="UTF-8"?>'
        new_content += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">' 
        new_content += '<en-note>' + div_contents + body + '</en-note>'   

        # Update note
        updated_note = Types.Note()
        updated_note.guid = to_str(note['guid'])    # Set the GUID. Must
        updated_note.title = to_str(note['title'])  # Set the title. Must
        updated_note.content = to_str(new_content)  # Set the new content
        note_store.updateNote(updated_note)

        # Update app data
        new_note = note_store.getNote(note['guid'], False, False, False, False)
        note['updated'] = False
        note['updateSequenceNum'] = new_note.updateSequenceNum
        note['notebook']['guid'] = new_note.notebookGuid
        note['notebook']['name'] = note_store.getNotebook(new_note.notebookGuid).name


def main(client):
    global note_data
    try:
        filename = here + '/note_data.json'
        with open(filename, 'rb') as f:
            note_data = json.load(f)
            
        # Initialize
        # client = EvernoteClient(token=token, sandbox=False, china=False)
        # user_store = client.get_user_store()
        note_store = client.get_note_store()
        # user = user_store.getUser()
        checkDataFile(note_store)
    
        # 2. Update Confirmation Procedure
        if checkNotebooksUpdate(note_store):    
            storeMetadata(note_store)
        else:
            return (True, 'No update')

        # 3. Notes Updating Procedure
        eNoteUpdate(note_store)
        note_data['updateCount'] = note_store.getSyncState().updateCount

        # 4. Save note_data
        with open(here + '/note_data.json', 'wb') as f:
            json.dump(note_data, f)
        
        return (True, 'Completed')

    except IOError as e:
        if e.filename == filename:
            print e
            print 'File missing. Run \'MakeContents.py\''
        return (False, e)

    except Errors.EDAMUserException as e:
        err = EDAMErrorCode._VALUES_TO_NAMES[e.errorCode] 
        param = e.parameter
        msg = 'Authentication failed. {} - {}'.format(err, param)
        return (False, msg)
        
    except Exception as e:
        msg = 'MakeContents App failed. {}'.format(e)
        return (True, msg)
    
    finally:
        with open(here + '/note_data.json', 'wb') as f:
            json.dump(note_data, f)

# if __name__ == '__main__':
#     main()
