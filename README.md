Description
===========
This is a Web App to make a table of contents in each Evernote's note.  
Bold strings that are presented in a note will be collected and displayed in the top of the note.  

ex.  

**CONTENTS**  
**Section 1**  
**Section 2**  
---
**Section 1**  
* List1
* List2
* List3  
    
**Section 2**  
* List1
* List2
* List3
    
How to use
--------
Run **MakeJson.py** with your **consumer_key**, **consumer_secret** and **notebook_name**.  
  
Run the server by  
```DIGITAL Command Language
python -m empj.makecontents.Server.py
```    
or **Server_MakeContents.bat**  

Add a tag named 'MakeContents' to target notes in the notebooks  

Access http://localhost:8080 
