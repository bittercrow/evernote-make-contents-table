Description
===========
This is a Web App to make a table of contents in each Evernote's note.  
Bold strings that are presented in a note will be collected and displayed in the top of the note.  

<details>  
    <summary>ex.</summary>
        <strong>CONTENTS</strong><br>  
        <strong>Section 1</strong><br>  
        <strong>Section 2</strong><br> 
        <div><hr/></div>
        <strong>Section 1</strong><br>
    <ul><li><div>List1</div></li></ul><br>
        <ul><li><div>List2</div></li></ul><br>
        <ul><li><div>List3</div></li></ul><br>
        <strong>Section 2</strong><br>
        <ul><li><div>List1</div></li></ul><br>
        <ul><li><div>List2</div></li></ul><br>
        <ul><li><div>List3</div></li></ul><br>
</details>      

How to use
==========
Initially, run **MakeJson.py** with your **consumer_key**, **consumer_secret** and **notebook_name**.  
  
Run the server by  
```DIGITAL Command Language
python -m empj.makecontents.Server.py
```    
or **Server_MakeContents.bat**  

Add a tag named 'MakeContents' to target notes in the notebooks  

Access http://localhost:8080 
